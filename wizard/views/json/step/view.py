import json
from copy import deepcopy

from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from wizard.views.json.step.base import WizardJsonStepBase
from wizard.views.json.step.exceptions import RequiredFieldsError


class WizardJsonStepView(WizardJsonStepBase):
    # override http_method_names = other methods return method_not_allowed()
    http_method_names = ['get', 'post']

    @staticmethod
    def add_cancel_if_draft(result, data, step):
        # a draft has been made. check whether we can cancel it
        if not data.get(step):
            return
        if data[step]['draft']:
            exclude = ['prev', 'next', 'draft']
            same = True
            # loop on both 'real' and 'draft' keys:
            real_keys = data[step]['real'].keys()
            draft_keys = data[step]['draft'].keys()
            try:
                merged = real_keys + draft_keys
            except TypeError:  # python 3 compatibility
                merged = set(real_keys) | set(draft_keys)
            for k in merged:
                if k not in exclude:
                    if data[step]['real'].get(k) != data[step]['draft'].get(k):
                        same = False
                        break
            if not same:  # ok to show cancel button:
                result['cancel'] = True

    @staticmethod
    def data_without_draft_or_real(data, step):
        # ! reconstruction of data without 'draft' and 'real' keys:
        if not data:
            return data
        result = deepcopy(data)
        # remove all 'draft' and 'real' keys:
        # first remove the only special key = 'breadcrumb':
        breadcrumb = deepcopy(result['breadcrumb'])
        del result['breadcrumb']
        # then keep current value, if it was a draft:
        data_draft = result.get(step, {}).get('draft')
        if data_draft:
            result_step = deepcopy(data_draft)
        else:
            result_step = deepcopy(result.get(step, {}).get('real', {}))
        try:
            del result[step]
        except KeyError:
            pass
        # now keep only 'real' values:
        result = {x: result[x].get('real') for x in result}
        # and re-add current step + breadcrumb
        result[step] = result_step
        result['breadcrumb'] = breadcrumb
        return result

    @staticmethod
    def get_step(request, custom_uuid_fn=None):
        uuid_reference = uuid = WizardJsonStepView.uuid

        # ! to make custom keys (ex: [uuid]_[company]):
        if custom_uuid_fn:
            uuid = custom_uuid_fn(uuid_reference)

        from wizard.models.wz_user_step import WzUserStep as Wus
        wz_user_step, created = Wus.objects.get_or_create(
            user=request.user,
            uuid_reference=uuid_reference,
            uuid=uuid)

        # generate a dict with key="step" and value="class to generate":
        tab = WizardJsonStepView.tab
        if wz_user_step.step and wz_user_step.step in tab:
            instance_class_step = tab[wz_user_step.step]()
        else:  # should never happen, but just in case: take the first one:
            first_key = sorted(tab.keys())[0]
            instance_class_step = tab[first_key]()
            if created:  # first time we come here -> create with the first key:
                wz_user_step.step = first_key
                wz_user_step.save()

        data = wz_user_step.data
        data = json.loads(data) if data else {}
        return wz_user_step, created, instance_class_step, data

    @method_decorator(ensure_csrf_cookie)  # !! Force csrf cookie creation !!
    def get(self, request, *args, **kwargs):
        # kwargs['company'] exists (otherwise error in CompanySelectedMixin)
        # kwargs['uuid'] *must* exist
        uuid, tab = self.initialize_uuid(**kwargs)
        if uuid is None or not request.user.is_authenticated:
            return JsonResponse({}, safe=False)
        if tab is None:
            return JsonResponse({}, safe=False)

        # here create custom uuid to look in the database:
        # format is "[uuid]_[company]" so there's one unique wizard per company:
        wz_user_step, created, step_instance, data = self.get_step(
            request,
            lambda _uuid: '{}_{}'.format(_uuid, kwargs['company']))
        breadcrumb = data.get('breadcrumb', {})
        step = wz_user_step.step

        # is_draft = self.is_draft(data, step)  # big comment in self.is_draft()
        data_draft = data.get(step, {}).get('draft')
        if data_draft:
            is_draft = data_draft != data.get(step, {}).get('real')
        else:
            is_draft = False

        from wizard.models.wz_user_step import WzUserStep as Wus
        data_without_draft_or_real = self.data_without_draft_or_real(data, step)
        try:
            title = step_instance.title
        except AttributeError:
            title = Wus.WZ_DEFAULT_TITLE
        result = {
            'title': title,
            'step': step,
            'content': step_instance.get_content(
                request, wz_user_step, data_without_draft_or_real, **kwargs),
            'breadcrumb': {
                'generic': [k.get('generic') for k in breadcrumb],
                'detail': [k.get('detail') for k in breadcrumb],
                'step': [k.get('step') for k in breadcrumb],
            },
        }
        ajax_data = step_instance.get_ajax_data(request, wz_user_step,
                                                data_without_draft_or_real,
                                                **kwargs)
        if ajax_data is not None:
            result['ajax_data'] = ajax_data
        self.add_cancel_if_draft(result, data, step)
        # ! last verification: check if 'real' is different from 'draft'
        return JsonResponse(result, safe=False)

    def post(self, request, *args, **kwargs):
        uuid, tab_step = self.initialize_uuid(**kwargs)
        if uuid is None or not request.user.is_authenticated:
            return JsonResponse({}, safe=False)

        # If we arrive here, the csrf is ok -> analyze the required values.

        # Analyze:
        # - what we should expect (= depending on the step in database)
        # - what is coming (= depending on the POST)

        # debug :
        # for key, value in request.POST.items():
        #     if 'csrf' not in key:  # ignore csrf information
        #         print('key = {}, value = {}'.format(key, value))

        prev_step = request.POST.get('prev')
        next_step = request.POST.get('next')
        draft_step = request.POST.get('draft')

        # Read the current step...
        # here create custom uuid to look in the database:
        # format is "[uuid]_[company]" so there's one unique wizard per company:
        wz_user_step, created, class_step, data = self.get_step(
            request,
            lambda _uuid: '{}_{}'.format(_uuid, kwargs['company']))

        # ...and pass parameters to the corresponding class
        # which should act upon and return the new step:
        if prev_step:
            fn_set_step = class_step.set_prev_step
            new_step = prev_step
        elif next_step:
            fn_set_step = class_step.set_next_step
            new_step = next_step
        elif draft_step:
            fn_set_step = class_step.set_draft_step
            new_step = draft_step
        else:  # hack
            return JsonResponse({}, safe=False)

        step = wz_user_step.step
        try:
            success, new_user_step, breadcrumb_detail, new_data, result = \
                fn_set_step(new_step=new_step,
                            request=request,
                            data=self.data_without_draft_or_real(data, step),
                            **kwargs)
        except RequiredFieldsError as e:
            success = False
            new_data = new_user_step = breadcrumb_detail = None
            result = class_step.message(is_get=False, message=e.message,
                                        title=e.title, abnormal=e.abnormal,
                                        message_fields=e.error_fields)

        if success and wz_user_step.step in tab_step:
            # ! we write to db here because we dont want the class_step to do
            #   this (it would duplicate the code for each class_step):

            # ! reload (in case it has been modified in-between)
            # here create custom uuid to look in the database: format is
            # "[uuid]_[company]" so there's one unique wizard per company:
            wz_user_step, created, instance_class_step, data = self.get_step(
                request,
                lambda _uuid: '{}_{}'.format(_uuid, kwargs['company']))

            step = wz_user_step.step
            if next_step:
                if not data.get(step):
                    data[step] = {'draft': {}, 'real': {}}
                data[step]['real'] = new_data
                data[step]['draft'] = {}
            elif new_step == draft_step:  # draft -> remember:
                if not data.get(step):
                    data[step] = {'draft': {}, 'real': {}}
                data[step]['draft'] = new_data
            else:  # clicked on 'previous' -> ignore modifications:
                pass

            # modify the breadcrumb
            breadcrumb = data.get('breadcrumb', [])
            # remove last step only if we actually changed:
            if prev_step and wz_user_step.step != new_user_step:
                if len(breadcrumb):
                    breadcrumb.pop()
            elif next_step and breadcrumb_detail is not None:
                # add new step if not None:
                breadcrumb.append({
                    'generic':
                    # (!) force translation:
                        str(tab_step[wz_user_step.step]().breadcrumb),
                    'detail': breadcrumb_detail,
                    'step': wz_user_step.step
                })
            data['breadcrumb'] = breadcrumb

            if new_user_step != 'draft':
                wz_user_step.step = new_user_step

            wz_user_step.data = json.dumps(data)
            wz_user_step.save()
        elif wz_user_step.step not in tab_step:
            # only happens if someone changed the key indexes
            # but it should never happen:
            result = class_step.message(is_get=False,
                                        message=str(_("Index not found")),
                                        abnormal=True)
        if result.get('success') and new_step == draft_step:
            self.add_cancel_if_draft(result, data, step)

        return JsonResponse(result, safe=False)
