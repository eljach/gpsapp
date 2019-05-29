import os
import tempfile
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.views.generic import View, ListView
from import_export.resources import modelresource_factory
from import_export.formats import base_formats
from import_export.forms import ImportForm, ConfirmImportForm
from .models import Position, Employee
from .resources import PositionResource

class EmployeeListView(ListView):
    model = Employee
    context_object_name = 'employee_list'

#@method_decorator(login_required, name='dispatch')
class PositionsImport(View):
    model = Position
    from_encoding = "utf-8"

    #: import / export formats
    DEFAULT_FORMATS = (
        base_formats.CSV,
        base_formats.XLS,
    )
    formats = DEFAULT_FORMATS
    #: template for import view
    import_template_name = 'reports/import_positions.html'
    resource_class = PositionResource

    def get_import_formats(self):
        """
        Returns available import formats.
        """
        return [f for f in self.formats if f().can_import()]

    def get_resource_class(self):
        """
        Automatically creates a resources class if it was not specified
        """
        if not self.resource_class:
            return modelresource_factory(self.model)
        else:
            return self.resource_class

    def get_import_resource_class(self):
        """
        Returns ResourceClass to use for import.
        """
        return self.get_resource_class()

    def get(self, *args, **kwargs ):
        '''
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        '''
        resource = self.get_import_resource_class()()

        context = {}

        import_formats = self.get_import_formats()
        form = ImportForm(import_formats,
                          self.request.POST or None,
                          self.request.FILES or None)

        if self.request.POST and form.is_valid():
            input_format = import_formats[
                int(form.cleaned_data['input_format'])
            ]()
            import_file = form.cleaned_data['import_file']
            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            with tempfile.NamedTemporaryFile(delete=False) as uploaded_file:
                for chunk in import_file.chunks():
                    uploaded_file.write(chunk)

            # then read the file, using the proper format-specific mode
            with open(uploaded_file.name,
                      input_format.get_read_mode()) as uploaded_import_file:
                # warning, big files may exceed memory
                data = uploaded_import_file.read()
                if not input_format.is_binary() and self.from_encoding:
                    data = force_text(data, self.from_encoding)
                dataset = input_format.create_dataset(data)
                result = resource.import_data(dataset, dry_run=True,
                                              raise_errors=True)

            context['result'] = result

            if not result.has_errors():
                context['confirm_form'] = ConfirmImportForm(initial={
                    'import_file_name': os.path.basename(uploaded_file.name),
                    'original_file_name': uploaded_file.name,
                    'input_format': form.cleaned_data['input_format'],
                })
            else:
                print ("RESULT: {}".format(result))

        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = [f.column_name for f in resource.get_fields()]
        context.update(self.kwargs)

        return TemplateResponse(self.request, [self.import_template_name], context)


    def post(self, *args, **kwargs ):
        '''
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        '''
        resource = self.get_import_resource_class()()#
        context = {}

        import_formats = self.get_import_formats()
        form = ImportForm(import_formats,
                          self.request.POST or None,
                          self.request.FILES or None)


        if self.request.POST and form.is_valid():
            input_format = import_formats[
                int(form.cleaned_data['input_format'])
            ]()
            import_file = form.cleaned_data['import_file']
            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            with tempfile.NamedTemporaryFile(delete=False) as uploaded_file:
                for chunk in import_file.chunks():
                    uploaded_file.write(chunk)

            # then read the file, using the proper format-specific mode
            with open(uploaded_file.name,
                      input_format.get_read_mode()) as uploaded_import_file:
                # warning, big files may exceed memory
                data = uploaded_import_file.read()
                if not input_format.is_binary() and self.from_encoding:
                    data = force_text(data, self.from_encoding)
                dataset = input_format.create_dataset(data)
                result = resource.import_data(dataset, dry_run=True,
                                              raise_errors=True)
            context['result'] = result

            if not result.has_errors():
                context['confirm_form'] = ConfirmImportForm(initial={
                    'import_file_name': os.path.basename(uploaded_file.name),
                    'original_file_name': uploaded_file.name,
                    'input_format': form.cleaned_data['input_format'],
                })
            else:
                print ("RESULT: {}".format(result))

        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = [f.column_name for f in resource.get_fields()]
        context.update(self.kwargs)
        return TemplateResponse(self.request, [self.import_template_name], context)

class PositionsProcessImport(View):
	model = Position
	from_encoding = "utf-8"

	#: import / export formats
	DEFAULT_FORMATS = (
		base_formats.CSV,
		base_formats.XLS,
	)
	formats = DEFAULT_FORMATS
	#: template for import view
	import_template_name = 'reports/import_positions.html'
	resource_class = PositionResource

	def get_import_formats(self):
		"""
		Returns available import formats.
		"""
		return [f for f in self.formats if f().can_import()]

	def get_resource_class(self):
		if not self.resource_class:
			return modelresource_factory(self.model)
		else:
			return self.resource_class

	def get_import_resource_class(self):
		"""
		Returns ResourceClass to use for import.
		"""
		return self.get_resource_class()

	def post(self, *args, **kwargs):
		'''
		Perform the actual import action (after the user has confirmed he
	wishes to import)
		'''
		opts = self.model._meta
		resource = self.get_import_resource_class()()

		confirm_form = ConfirmImportForm(self.request.POST)
		if confirm_form.is_valid():
			import_formats = self.get_import_formats()
			input_format = import_formats[
				int(confirm_form.cleaned_data['input_format'])
			]()
			import_file_name = os.path.join(
				tempfile.gettempdir(),
				confirm_form.cleaned_data['import_file_name']
			)
			import_file = open(import_file_name, input_format.get_read_mode())
			data = import_file.read()
			if not input_format.is_binary() and self.from_encoding:
				data = force_text(data, self.from_encoding)
			dataset = input_format.create_dataset(data)
			result = resource.import_data(dataset, dry_run=False,
								 raise_errors=True)

			import_file.close()
            #redirect to reporst visualization view
			#return redirect(reverse('presale_splash', kwargs=redirect_kwargs))
		else:
			print (confirm_form.errors)
