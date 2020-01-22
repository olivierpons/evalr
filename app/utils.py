from django.contrib import messages


def add_messages(request, title, all_messages,
                 level=messages.SUCCESS,
                 extra_tags='',
                 fail_silently=False):
    messages.add_message(request, level, title, extra_tags, fail_silently)
    for message in all_messages:
        messages.add_message(request, level, message, extra_tags, fail_silently)
