from django.contrib import admin
from .models import (
    UserProfile, Train, Coach, LinenItem, LinenAssignment,
    LinenLifecycleEvent, CollectionSession, CollectionScan, CoachHandOff
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'badge_number')
    list_filter = ('role',)


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ('train_number', 'train_name', 'source', 'destination')
    search_fields = ('train_number', 'train_name')


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ('train', 'coach_number', 'coach_type')
    list_filter = ('train', 'coach_type')


class LinenLifecycleEventInline(admin.TabularInline):
    model = LinenLifecycleEvent
    extra = 0
    readonly_fields = ('timestamp', 'event_type', 'location', 'performed_by', 'notes')
    can_delete = False


@admin.register(LinenItem)
class LinenItemAdmin(admin.ModelAdmin):
    list_display = ('linen_code', 'linen_type', 'status', 'current_location', 'updated_at')
    list_filter = ('status', 'linen_type')
    search_fields = ('linen_code', 'qr_code')
    inlines = [LinenLifecycleEventInline]


@admin.register(LinenAssignment)
class LinenAssignmentAdmin(admin.ModelAdmin):
    list_display = ('linen', 'train', 'coach', 'berth', 'passenger_reference', 'assignment_status', 'issued_at')
    list_filter = ('assignment_status', 'train', 'coach')
    search_fields = ('linen__linen_code', 'passenger_reference')


@admin.register(LinenLifecycleEvent)
class LinenLifecycleEventAdmin(admin.ModelAdmin):
    list_display = ('linen', 'event_type', 'location', 'timestamp', 'performed_by')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('linen__linen_code', 'location')


class CollectionScanInline(admin.TabularInline):
    model = CollectionScan
    extra = 0
    readonly_fields = ('scanned_qr', 'result', 'scanned_at', 'scanned_by', 'message')
    can_delete = False


@admin.register(CollectionSession)
class CollectionSessionAdmin(admin.ModelAdmin):
    list_display = ('train', 'coach', 'attender', 'started_at', 'expected_quantity', 'scanned_quantity', 'missing_quantity', 'status')
    list_filter = ('status', 'train')
    inlines = [CollectionScanInline]


@admin.register(CollectionScan)
class CollectionScanAdmin(admin.ModelAdmin):
    list_display = ('collection_session', 'scanned_qr', 'result', 'scanned_at', 'scanned_by')
    list_filter = ('result', 'scanned_at')


@admin.register(CoachHandOff)
class CoachHandOffAdmin(admin.ModelAdmin):
    list_display = ('attendant', 'train', 'coach', 'shift', 'bedsheets_handed_over', 'status', 'date')
    list_filter = ('status', 'shift', 'train')

