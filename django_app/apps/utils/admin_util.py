from django.db.models import Q


from users.models import UserGroup, Group, UserProfile

def find_organization_admin_users(organization_id):
    """
    Find all admin users for an organiztion
    :param int organization_id: organization id
    :return list: users who have permission to approve create group requests in the organization
    """
    result = []
    # find the admin group in the organization
    try:
        admin_group = Group.objects.filter(organization_id=organization_id, is_admin=True).get()
        for x in UserGroup.objects.filter(Q(role=2)|Q(role=3), group=admin_group).all():
            result.append(x.user)
    except:
        pass
    if not result:
        # find site admin if we have not found organization admins
        for x in UserProfile.objects.filter(is_staff=True).all():
            result.append(x)
    return result


def find_group_admin_users(group_id):
    """
    Find all admin users for group
    :param int group_id: group id
    :return list: users who have permission to approve join/leave requests for the group
    """
    result = []
    # first find all admin or teacher in the group
    for x in UserGroup.objects.filter(Q(role=2)|Q(role=3), group_id=group_id).all():
        result.append(x.user)

    if not result:
        # there's no admin for the group? then find admin for the organization
        group = Group.objects.filter(id=group_id).get()
        result = find_organization_admin_users(group.organization_id)
    return result


def find_site_admin_user():
    """
    Find site admin user
    :return:
    """
    return UserProfile.objects.filter(is_staff=True).all()[0]
