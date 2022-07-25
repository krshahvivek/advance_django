# custom permissions
import re
from rest_framework import permissions

class IsStaffEditorPermission(permissions.DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }
    def has_permission(self, request, view):
        if not request.user.is_staff:
            return False
        return super().has_permission(request, view)
    # def has_permission(self, request, view):
    #     user = request.user
    #     print(user.get_all_permissions())   
    #     # it is doing some sort of permission but not like that it should,
    #     #because if any user has any permission from below, it is going to be true always.
    #     # that's why this custom permission is not efficient, and we want specific permission for each perticular view
    #     if user.is_staff:
    #         if user.has_param("product.add_product"):
    #             return True
    #         if user.has_param("product.delete_prodcut"):
    #             return True
    #         if user.has_param("product.change_product"):
    #             return True
    #         if user.has_param("product.view_product"):
    #             return True
    #         return False
    #     return False

    # def has_object_permission(self, request, view, obj):
    #     return obj.owner == request.user