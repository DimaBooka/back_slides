from rest_framework.fields import FileField


class SlidesUrlAndFileField(FileField):
    FileField.default_error_messages['big_file'] = 'File is bigger than 2 MB'

    def to_internal_value(self, data):

        try:
            # `UploadedFile` objects should have name and size attributes.
            file_name = data.name
            file_size = data.size
        except AttributeError:
            return data

        if not file_name:
            self.fail('no_name')
        if not self.allow_empty_file and not file_size:
            self.fail('empty')
        if self.max_length and len(file_name) > self.max_length:
            self.fail('max_length', max_length=self.max_length, length=len(file_name))
        if file_size > 2097152:
            self.fail('big_file')

        return data
