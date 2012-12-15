from django.dispatch import receiver
from inyoka.forum.models import Attachment
from inyoka.markup import nodes
from inyoka.wiki.signals import build_picture_node


@receiver(build_picture_node)
def build_forum_picture_node(sender, context, format, **kwargs):
    if not context.application == 'forum':
        return

    target, width, height = (sender.target, sender.width, sender.height)

    try:
        # There are times when two users upload a attachment with the same
        # name, both have post=None, so we cannot .get() here
        # and need to filter for attachments that are session related.
        # THIS IS A HACK and should go away once we found a way
        # to upload attachments directly to bound posts in a sane way...

        forum_post = context.kwargs.get('forum_post', None)
        post = forum_post.id if forum_post else None

        if context.request and 'attachments' in context.request.POST:
            att_ids = map(int, filter(bool,
                context.request.POST.get('attachments', '').split(',')
            ))

            files = Attachment.objects.filter(name=target,
                    post=post, id__in=att_ids)
            return nodes.HTML(files[0].html_representation)
        else:
            file = Attachment.objects.get(name=target, post=forum_post)
            return nodes.HTML(file.html_representation)
    except (Attachment.DoesNotExist, IndexError):
        return