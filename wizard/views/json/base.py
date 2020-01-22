import re

import pytz
from django.conf.urls.static import static

from django.forms import CharField, TypedChoiceField
from django.forms.models import ModelChoiceField
from django.forms.widgets import Textarea
from django.utils.timezone import now, make_aware
from django.utils.translation import ugettext_lazy as _

from wizard.views.json.step.exceptions import RequiredFieldsError


class WizardBase(object):

    incorrect_step = {'success': False, 'message': _("Incorrect step")}

    @staticmethod
    def print_data(data):
        from pprint import pprint
        print('data')
        for key in sorted(data.keys()):
            print('*' * 45)
            print(key)
            pprint(data[key])

    def incorrect_step_result(self):
        return False, -1, None, None, self.incorrect_step

    @staticmethod
    def message(is_get, message, title=None, abnormal=False,
                message_fields=None):
        """
        Returns a message that will be displayed to the user

        Args:
            is_get: if the error is called from "get" step or "post" step
            message: the message to display
            title: if there's a title (ignored for "post" step)
            abnormal: if it's a internal (= unexpected) error
            message_fields: fields to be handled by jquery

        Returns:
            Message that will be displayed to the user
        """
        if message_fields is None:
            message_fields = {}
        _title = title
        _message = message
        if abnormal:
            _message = _("Internal error: {}").format(message)
            if not title:
                _title = _("Internal error")
                _message = _("Technical details:") + '\n\n' + \
                    message + '\n\n' + \
                    _("We're sorry for the inconvenience")
        if not is_get:
            if not message_fields:
                return {'success': False,
                        'title': _title,
                        'message': _message}
            else:
                return {'success': False,
                        'title': _title,
                        'message': _message,
                        'message_fields': message_fields}
        result = []
        if _title:
            result.append({'type': 'text',
                           'data': [{'type': 'title_2', 'content': _title}]})
        result.append(
            {'type': 'text',
             'data': [
                 {'type': 'title_5',
                  'class': 'warning',
                  'content': _message},
             ]})
        result.append(
            {'type': 'buttons',
             'data': {'reload': True, }})
        if message_fields:
            result.append({'type': 'message_fields',
                           'data': message_fields})
        return result

    @staticmethod
    def error_message(is_get, message, title=None, abnormal=False,
                      message_fields=None):
        """
        Returns an error message that will be displayed to the user

        Args:
            is_get: if the error is called from "get" step or "post" step
            message: the message to display
            title: if there's a title (ignored for "post" step)
            abnormal: if it's a internal (= unexpected) error
            message_fields: fields to be handled by jquery

        Returns:
            Error message that will be displayed to the user
        """
        if message_fields is None:
            message_fields = {}
        if not is_get:
            return False, -1, None, None, WizardBase.message(is_get, message,
                                                             title, abnormal,
                                                             message_fields)
        return WizardBase.message(is_get, message, title,
                                  abnormal, message_fields)

    @staticmethod
    def make_reset_button():
        """
        Makes a reset button. Button to be added after wizard has been finished.

        Returns:
            Dict to be sent with the answer
        """
        label_restart = _("Reset wizard")
        img_url = static('icons/refresh-white.png')
        return {
            'type': 'text',
            'data': [{'type': 'title_4',
                      'class': 'buttons-prev-next-bottom disable-select',
                      'line_break': False,
                      'content': [
                          {'type': 'link',
                           'line_break': False,
                           'data': {
                               'class': 'button',
                               'content': [{'type': 'image',
                                            'data': {
                                                'src': img_url,
                                                'alt': label_restart,
                                                'title': label_restart,
                                                'width': '11px',
                                                'height': '11px',
                                            }}, ' ',
                                           _("Restart a new wizard"), ],
                               # hard coded in the wizard:
                               'callback': 'reset',
                           }},
                      ]}]}

    @staticmethod
    def _add_if_set(f, key, dest):
        val = f.get(key)
        if val is not None:
            dest[key] = val

    @staticmethod
    def check_post_missing_field(post_vals, key, is_boolean):
        """ Checks if a key is missing from post
        If key is for a boolean, it tests also the 'false" string value

        Args:
            post_vals: POST data
            key: key to check
            is_boolean: must be True if the key refers to a boolean attribute

        Returns:
            True if field is missing in POST
        """
        return (not post_vals.get(key) or
                (is_boolean and post_vals.get(key, 'false').lower() == 'false'))

    @staticmethod
    def get_post_values(request, filter_no_values=True, keep_empty=False):
        """
        Get all interesting values from the POST (= without csrf information)

        Args:
            request: the request
            filter_no_values: ignore POST value if they're "no"
            keep_empty: keep POST value even if it's ''
                        (for models that accept '' but don't accept null)

        Returns:
            array of filtered values, value of the host chosen
        """
        def none_if_no(v):
            if keep_empty and v == '':
                return ''
            if v in ['', '-', 'no', None]:  # possibilities that mean "NO"
                return None
            # we can get stuff like "ComplexMixin", "OtherMixin", etc.
            # -> split a string at uppercase letters:
            s = re.findall('[A-Z][^A-Z]*', v)
            if len(s):
                if s[0].lower() == 'no':
                    return None
            return v

        # cleanup the POST values to save them:
        vals = {}
        for key, value in request.POST.items():
            if 'csrf' not in key:  # ignore csrf information
                cleaned_data = none_if_no(value) if filter_no_values else value
                if cleaned_data is not None:
                    vals[key] = cleaned_data
        # handle POST required parameters
        return vals

    @staticmethod
    def get_ajax_data(request, wz_user_step, data, **kwargs):
        """
        Function that should return values to be used to populate fields
        when restoring a step which has AJAX calls

        Args:
            request: the request
            wz_user_step: current wz_user_step model
            data: all data gathered step after step
            **kwargs: other arguments (company and uuid amongst others)

        Returns:
            Object that should be returned as JSON or None
        """
        return None

    def set_next_step(self, new_step, request, data, **kwargs):
        """
        Analyze parameters and if it's ok returns the next step
        (*without modifying database*)

        Args:
            new_step: new_step (coming from user choice)
            request: the request
            data: all data gathered step after step
            **kwargs: other arguments (company and uuid amongst others)

        Returns:
            5 values:
                - success: True or False if success,
                - new_user_step: New step (ignored if success == False)
                - breadcrumb_detail: Detail to show (summary of choices done)
                - db_data: Data to remember into database (if any)
                - result: Object to JSON-encode for the AJAX result
        """
        return False, -1, None, None, {'success': False, }

    def set_draft_step(self, request, data, **kwargs):
        """
        Analyze parameters and if it's ok returns the new step
        (*without modifying database*)

        Args:
            request: the request
            data: all data gathered step after step
            **kwargs: other arguments (company and uuid amongst others)

        Returns:
            5 values:
                - success: True or False if success,
                - new_user_step: New step (ignore if success == False),
                - breadcrumb_detail: Detail to show (summary of choices done)
                - db_data: Data to remember into database (if any)
                - result: Object to JSON-encode for the AJAX result
        """
        # remove 'new_step' arg because we manually precise it:
        new_kwargs = {k: v for k, v in kwargs.items() if k != 'new_step'}
        success, new_user_step, breadcrumb_detail, db_data, result = \
            self.set_next_step(new_step='draft',  # hard coded
                               request=request,
                               data=data, **new_kwargs)

        return success, 'draft', breadcrumb_detail, db_data, result

    @staticmethod
    def injection_dates_description(data, step):
        data_i = data.get(step, {}) or {}
        injection_dates = data_i.get('injection_dates')
        if not injection_dates:
            return None
        if len(injection_dates) > 1:
            return [u'', _("Dates and times of all injections:")] + \
                   [u'- {}'.format(a) for a in injection_dates]
        return [_("Injection done: {}").format(injection_dates[0])]

    @staticmethod
    def injection_dates_add(data, step):
        """
        Function that adds a new injection date to the current dictionary.

        Args:
            data: all data gathered step after step
            step: the step where the injection dates is supposed to be

        Returns:
            The data dict updated
        """
        n = make_aware(now(), pytz.timezone('Europe/Paris'))
        str_datetime = n.strftime('%d-%m-%Y, %H:%M:%S')

        data_i = data.get(step, {}) or {}
        injection_dates = data_i.get('injection_dates', [])
        injection_dates.append(str_datetime)
        return str_datetime, injection_dates

    @staticmethod
    def make_cell_with_data(cell_type, data):
        return {'type': cell_type,
                'data': data}

    def make_cell(self, cell_type, text, italic=False, line_break=True):
        data = {'type': 'text',
                'content': text}
        if italic:
            data['italic'] = True
        if not line_break:  # only precise when we dont want line breaks:
            data['line_break'] = False
        return self.make_cell_with_data(cell_type, [{'type': 'text',
                                                     'data': [data]}])

    @staticmethod
    def make_text(text_type='p', text_content='', text_class=''):
        # 'important warning'
        if not text_content:
            return {}
        result = {'type': text_type,
                  'content': text_content}
        if text_class:
            result['class'] = text_class
        return result

    @staticmethod
    def modelform_fields_check_post(instance, prefix, post_values, **kwargs):
        """
        Check in the incoming post values that we have all required fields.
        Otherwise

        Args:
            instance: and instance of a ModelForm
            prefix: the prefix to add to all fields of the ModelForm
            post_values: the post values (have to be clean)
            **kwargs: other arguments (company amongst others)

        Returns:

        """
        error_message = []
        error_fields = {}
        for name, field in instance.fields.items():
            p_name = '{}_{}'.format(prefix, name)
            if field.widget.is_required:
                if not post_values.get(p_name):
                    error_fields[p_name] = _("Select/fill a value")
                    error_message.append(
                        _("Select/fill a value for {}").format(field.label))

        if error_message:
            raise RequiredFieldsError(is_get=False, abnormal=False,
                                      title=_("Mandatory fields"),
                                      message=error_message,
                                      error_fields=error_fields)

    # noinspection PyTypeChecker
    @staticmethod
    def modelform_fields_get(instance, prefix, **kwargs):
        result = []
        for name, field in instance.fields.items():
            if prefix:
                p_name = '{}_{}'.format(prefix, name)
            else:
                p_name = name
            if isinstance(field, CharField):
                if isinstance(field.widget, Textarea):
                    to_add = {'type': 'input_textarea', }
                else:
                    to_add = {'type': 'input', }
                to_add['data'] = {'input_type': 'text', }
            elif isinstance(field, ModelChoiceField) or \
                    isinstance(field, TypedChoiceField):
                choices = field.choices

                to_add = {'type': 'select',
                          # a select radio *must have* an id:
                          'id': p_name,
                          'name': p_name,
                          'data': {
                              'class': 'select-vertical-align',
                              'options': [
                                  {'id': '{}_{}'.format(p_name, idx),
                                   'label': _(pair[1]),
                                   'value': pair[0],
                                   'selected': (idx == 0),
                                   }
                                  for idx, pair in enumerate(choices)]}}
            else:
                raise Exception(
                    _("Type of model not handled {}").format(field))
            # ! here's my logic: I look for all the properties of
            #   what should be DISPLAYED = for the user => widget attrs
            #   and *NOT* the model itself (which could differ):
            val = field.widget.attrs.get('minlength')
            if val:
                to_add['data']['min_length'] = int(val)
            val = field.widget.attrs.get('maxlength')
            if val:
                to_add['data']['max_length'] = int(val)
            if field.widget.is_required:
                to_add['data']['required'] = True

            # common values for all type of input:
            to_add['data']['id'] = p_name
            to_add['data']['name'] = p_name
            to_add['data']['to_send'] = True
            to_add['data']['label'] = field.label
            to_add['data']['wrapper'] = 'p'
            result.append(to_add)

        return result

    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")

    @staticmethod
    def is_email(text):
        if not isinstance(text, str):
            return False
        return WizardBase.email_regex.match(text)
