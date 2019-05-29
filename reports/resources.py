import datetime
from import_export import resources
from .models import Position, Employee

DELETABLE_COLUMN_NAMES = [
    'speed(mph)',
    'speed(km/h)',
    'altitude(ft)',
    'altitude(m)',
    'distance(mile)',
    'distance(km)',
    'date2',
    'address',
    'type',
    'visit',
]

class PositionResource(resources.ModelResource):
    def clean_dates(self, dataset):
        i = 0
        last = dataset.height - 1

        while i <= last:
            date = dataset['date'][0]
            cleaned_date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S %p')
            try:
                dataset.rpush(
                    tuple([cleaned_date if dataset.headers.index("date") == x else dataset.get_col(x)[0] for x in range(0, len(dataset.headers))])
                )
            except Exception as err:
                print (err)
            dataset.lpop()
            i = i + 1
        return dataset

    def clean_dataset(self, dataset):
        dataset.headers = [header.lower() for header in dataset.headers]
        dataset.headers = ["employee" if header == 'name' else header for header in dataset.headers]
        for column in DELETABLE_COLUMN_NAMES:
            try:
                dataset[column]
                del(dataset[column])
            except:
                pass
        dataset_with_cleaned_dates = self.clean_dates(dataset)
        return dataset_with_cleaned_dates

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        try:
            dataset["id"]
        except:
            try:
                dataset.append_col([None for row in range(len(dataset))], header='id')
            except:
                print ("An error ocurred when trying to append ID column to the dataset")
        cleaned_dataset = self.clean_dataset(dataset)

        i = 0
        last = cleaned_dataset.height - 1

        while i <= last:
            name = cleaned_dataset['employee'][0].lower()
            employee, created = Employee.objects.get_or_create(name=name)
            try:
                dataset.rpush(
                    tuple([employee.id if dataset.headers.index("employee") == x else dataset.get_col(x)[0] for x in range(0, len(dataset.headers))])
                )
            except Exception as err:
                print (err)
            dataset.lpop()
            i = i + 1
        print (cleaned_dataset)
        return cleaned_dataset

    class Meta:
        model = Position
        fields = (
            'id',
            'employee',
            'lat',
            'lng',
            'accuracy',
            'date',
        )
