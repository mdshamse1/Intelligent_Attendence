from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using a variable key"""
    if dictionary and key:
        return dictionary.get(key)
    return None

@register.filter
def get_attendance(attendance_dict, student_id):
    """Get attendance status for a student"""
    if attendance_dict and student_id:
        return attendance_dict.get(student_id, False)
    return False
