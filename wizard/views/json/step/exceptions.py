class RequiredFieldsError(Exception):

    def __init__(self, message, is_get=True, abnormal=False, title=None,
                 error_fields=None):
        super(RequiredFieldsError, self).__init__()
        self.message = message
        self.is_get = is_get
        self.abnormal = abnormal
        self.title = title
        self.error_fields = error_fields
