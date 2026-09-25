from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Root Dispatcher & Auth
    path('', views.root_dispatcher, name='root_dispatcher'),
    path('login/', views.demo_login, name='login'),
    path('logout/', views.demo_logout, name='logout'),

    # 4. Attendant App Routes
    path('attendant/', views.attendant_assignment, name='attendant_assignment'),
    path('attendant/assignment/', views.attendant_assignment, name='attendant_assignment_explicit'),
    path('attendant/hub/', views.attendant_hub, name='attendant_hub'),
    path('attendant/issue/', views.attendant_issue, name='attendant_issue'),
    path('attendant/alert/', views.attendant_alert, name='attendant_alert'),
    path('attendant/roster/', views.attendant_roster, name='attendant_roster'),
    path('attendant/collect/', views.attendant_collect, name='attendant_collect'),
    path('attendant/report/', views.attendant_end_report, name='attendant_end_report'),

    # 5. Laundry App Routes
    path('laundry/', views.laundry_register, name='laundry_dashboard'),
    path('laundry/register/', views.laundry_register, name='laundry_register'),
    path('laundry/intake/', views.laundry_intake, name='laundry_intake'),
    path('laundry/scanner/', views.laundry_intake, name='laundry_scanner'),

    # 6. Supervisor Console Routes
    path('supervisor/', views.supervisor_handoff, name='supervisor_handoff'),
    path('supervisor/handoff/', views.supervisor_handoff, name='supervisor_handoff_explicit'),
    path('supervisor/dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('dashboard/', views.supervisor_dashboard, name='dashboard'),
    path('attender/', views.attendant_hub, name='attender_root'),
    path('attender/dashboard/', views.attendant_hub, name='attender_dashboard'),
    path('attender/hub/', views.attendant_hub, name='attender_hub_alias'),
    path('attender/issue/', views.attendant_issue, name='attender_issue_alias'),
    path('attender/issue/<int:passenger_id>/', views.attendant_issue, name='attender_issue_id_alias'),
    path('attender/collect/', views.attendant_collect, name='attender_collect_alias'),
    path('attender/report/', views.attendant_end_report, name='attender_report_alias'),
    path('attender/alert/', views.attendant_alert, name='attender_alert_alias'),
    path('attender/roster/', views.attendant_roster, name='attender_roster_alias'),
    path('supervisor/settlement/', views.supervisor_settlement, name='supervisor_settlement'),
    path('supervisor/missing/', views.supervisor_settlement, name='supervisor_missing'),

    # Supervisor Reporting & Utilities
    path('reports/audit/', views.audit_log, name='audit_log'),
    path('reports/search/', views.global_search, name='global_search'),
    path('linen/<str:linen_code>/', views.linen_detail, name='linen_detail'),
    path('linen/<str:linen_code>/lifecycle/', views.linen_detail, name='linen_lifecycle'),
    path('linen/<str:linen_code>/qr.png', views.linen_qr_image, name='linen_qr_image'),
    path('linen/<str:linen_code>/print/', views.linen_qr_print, name='linen_qr_print'),

    # REST APIs (Strict RBAC enforced in api_views)
    path('api/collection/scan/', api_views.api_collection_scan, name='api_collection_scan'),
    path('api/collection/return/', api_views.api_mark_returned, name='api_collection_return'),
    path('api/collection/mark-returned/', api_views.api_mark_returned, name='api_mark_returned'),
    path('api/attendant/issue/', api_views.api_attendant_issue_linen, name='api_attendant_issue_linen'),
    
    path('api/laundry/register/', api_views.api_laundry_register, name='api_laundry_register'),
    path('api/laundry/generate/', api_views.api_laundry_generate, name='api_laundry_generate'),
    path('api/laundry/available-stock/', api_views.api_available_linen_stock, name='api_available_linen_stock'),
    path('api/laundry/receive/', api_views.api_laundry_receive, name='api_laundry_receive'),
    path('api/laundry/wash/', api_views.api_laundry_wash, name='api_laundry_wash'),
    path('api/laundry/reissue/', api_views.api_laundry_reissue, name='api_laundry_reissue'),

    path('api/supervisor/handoff/update/', api_views.api_supervisor_update_handoff, name='api_supervisor_update_handoff'),
    path('api/supervisor/assign-coach/', api_views.api_supervisor_assign_attendant, name='api_supervisor_assign_attendant'),
    path('api/supervisor/create-employee/', api_views.api_supervisor_create_employee, name='api_supervisor_create_employee'),
    path('api/supervisor/settlement/', api_views.api_supervisor_settlement_decision, name='api_supervisor_settlement_decision'),
    path('api/dashboard/stats/', api_views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/trains/<int:train_id>/coaches/', api_views.api_get_coaches, name='api_get_coaches'),
    path('api/pnr/<str:pnr_number>/', api_views.api_lookup_pnr, name='api_lookup_pnr'),
]
