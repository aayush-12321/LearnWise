from django import template
import mimetypes

register = template.Library()

@register.filter
def is_image(media):
    """
    Check if the file in the `image` field is an image based on its MIME type.
    """
    if hasattr(media, 'image') and media.image:
        mime = mimetypes.guess_type(media.image.url)[0]
        return mime and mime.startswith('image')
    return False

@register.filter
def is_video(media):
    """
    Check if the file in the `image` field is a video based on its MIME type.
    """
    if hasattr(media, 'image') and media.image:
        mime = mimetypes.guess_type(media.image.url)[0]
        return mime and mime.startswith('video')
    return False
