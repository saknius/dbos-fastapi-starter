from database.session import SessionLocal, Base, engine
from services.authorization.models.role import Role
from services.authorization.models.policy import Policy
from services.authorization.models.resource import Resource
from services.authorization.models.policy_resource import PolicyResource
from services.authorization.models.role_policy import RolePolicy

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create roles
    super_admin_role = Role(name="SuperAdmin")
    admin_role = Role(name="Admin")
    developer_role = Role(name="Developer")
    viewer_role = Role(name="Viewer")

    db.add_all([super_admin_role, admin_role, developer_role, viewer_role])
    db.commit()

    # Create policies
    manage_clusters_policy = Policy(name="manage_clusters", description="Manage clusters (create, update, delete)")
    deploy_applications_policy = Policy(name="deploy_applications", description="Deploy applications")
    view_resources_policy = Policy(name="view_resources", description="View clusters, deployments, and other resources")
    manage_organizations_policy = Policy(name="manage_organizations", description="Create, join, and list organizations")
    manage_tables_policy = Policy(name="manage_tables", description="Create and drop tables")

    db.add_all([manage_clusters_policy, deploy_applications_policy, view_resources_policy, manage_organizations_policy, manage_tables_policy])
    db.commit()

    # Register resources (APIs)
    resources = [
        Resource(path="/clusters/create_cluster", method="POST"),
        Resource(path="/core/create_tables", method="GET"),
        Resource(path="/core/drop_tables", method="GET"),
        Resource(path="/clusters/update_cluster", method="POST"),
        Resource(path="/deployments/create_deployment", method="POST"),
        Resource(path="/deployments/schedule_deployment", method="POST"),
        Resource(path="/deployments/complete_deployment", method="POST"),
        Resource(path="/user/create_user", method="POST"),
        Resource(path="/user/login_user", method="POST"),
        Resource(path="/organization/create_organization", method="POST"),
        Resource(path="/organization/list_organizations", method="GET"),
        Resource(path="/organization/join_organization", method="POST"),
    ]

    db.add_all(resources)
    db.commit()

    # Assign policies to resources based on resource path
    policy_resources = []

    # Create mapping of resource paths to policy assignments
    policy_resources_map = {
        manage_clusters_policy: ["/clusters/create_cluster", "/clusters/update_cluster"],
        deploy_applications_policy: ["/deployments/create_deployment", "/deployments/schedule_deployment", "/deployments/complete_deployment"],
        view_resources_policy: ["/user/create_user", "/user/login_user", "/organization/list_organizations", "/organization/join_organization"],
        manage_organizations_policy: ["/organization/create_organization", "/organization/list_organizations", "/organization/join_organization"],
        manage_tables_policy: ["/core/create_tables", "/core/drop_tables"],
    }

    # For each policy, find its resources and assign them dynamically
    for policy, paths in policy_resources_map.items():
        for path in paths:
            resource = db.query(Resource).filter(Resource.path == path).first()
            if resource:
                policy_resources.append(PolicyResource(policy_id=policy.id, resource_id=resource.id))

    db.add_all(policy_resources)
    db.commit()

    # Assign policies to roles
    role_policies = [
        # SuperAdmin role can access everything
        RolePolicy(role_id=super_admin_role.id, policy_id=manage_clusters_policy.id),
        RolePolicy(role_id=super_admin_role.id, policy_id=deploy_applications_policy.id),
        RolePolicy(role_id=super_admin_role.id, policy_id=view_resources_policy.id),
        RolePolicy(role_id=super_admin_role.id, policy_id=manage_organizations_policy.id),
        RolePolicy(role_id=super_admin_role.id, policy_id=manage_tables_policy.id),
        
        # Admin role policies
        RolePolicy(role_id=admin_role.id, policy_id=manage_clusters_policy.id),
        RolePolicy(role_id=admin_role.id, policy_id=deploy_applications_policy.id),
        RolePolicy(role_id=admin_role.id, policy_id=view_resources_policy.id),
        RolePolicy(role_id=admin_role.id, policy_id=manage_organizations_policy.id),
        RolePolicy(role_id=admin_role.id, policy_id=manage_tables_policy.id),
        
        # Developer role policies
        RolePolicy(role_id=developer_role.id, policy_id=deploy_applications_policy.id),
        RolePolicy(role_id=developer_role.id, policy_id=view_resources_policy.id),
        RolePolicy(role_id=developer_role.id, policy_id=manage_organizations_policy.id),
        
        # Viewer role policies
        RolePolicy(role_id=viewer_role.id, policy_id=view_resources_policy.id),
        RolePolicy(role_id=viewer_role.id, policy_id=manage_organizations_policy.id),
    ]

    db.add_all(role_policies)
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
