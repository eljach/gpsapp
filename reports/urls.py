from django.urls import path
from .views import PositionsImport, PositionsProcessImport, EmployeeListView

urlpatterns = [
    path("reports/import", PositionsImport.as_view(), name="import"),
    path("reports/process-import", PositionsProcessImport.as_view(), name="process_import"),
    path("reports/", EmployeeListView.as_view(), name="reports")
]
