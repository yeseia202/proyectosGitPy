#!/usr/bin/env python3
import os
import git
import argparse
from treelib import Node, Tree

# Configure Git executable explicitly if not in PATH
git.Git.refresh(path="/usr/bin/git")  # Change the path if necessary

def get_directory_structure(base_path):
    """Gets the directory structure and Git repository status."""
    structure = {}
    for client in os.listdir(base_path):
        client_path = os.path.join(base_path, client)
        if os.path.isdir(client_path):
            structure[client] = {}
            for project in os.listdir(client_path):
                project_path = os.path.join(client_path, project)
                if os.path.isdir(project_path):
                    structure[client][project] = {"repositories": {}}
                    repos_path = os.path.join(project_path, "repositories")
                    if os.path.exists(repos_path):
                        for repo_type in os.listdir(repos_path):
                            repo_type_path = os.path.join(repos_path, repo_type)
                            if os.path.isdir(repo_type_path):
                                structure[client][project]["repositories"][repo_type] = []
                                for branch in os.listdir(repo_type_path):
                                    branch_path = os.path.join(repo_type_path, branch)
                                    if os.path.isdir(branch_path):
                                        try:
                                            repo = git.Repo(branch_path)
                                            git_status = "Git initialized"
                                            try:
                                                last_commit = repo.head.commit
                                                commit_date = last_commit.authored_datetime
                                                commit_author = last_commit.author.name
                                                commit_message = last_commit.message
                                                git_status += f"\n  Last commit: {commit_date} by {commit_author}\nMessage: {commit_message}"
                                            except ValueError:
                                                git_status = "Empty repository"
                                        except git.exc.InvalidGitRepositoryError:
                                            git_status = "Not a Git repository"
                                        except Exception as e:
                                            git_status = f"Error retrieving Git status: {e}"

                                        structure[client][project]["repositories"][repo_type].append(
                                            {"branch": branch, "status": git_status}
                                        )
    return structure

def list_structure(structure):
    """Lists the directory structure with absolute URLs of branches."""
    for client, projects in structure.items():
        print(f"\nClient: {client}")
        for project, data in projects.items():
            print(f"  Project: {project}")
            for repo_type, branches in data["repositories"].items():
                print(f"    Repository: {repo_type}")
                for branch in branches:
                    absolute_path = os.path.join(base_path, client, project, "repositories", repo_type, branch['branch'])
                    print(f"      Branch: {branch['branch']}")
                    print(f"      URL: {absolute_path}")
                    print(f"      Status: {branch['status'].splitlines()[0]}")  # Show only the first line of the status

def show_summary(structure):
    """Shows a summary of the directory structure."""
    for client, projects in structure.items():
        print(f"\nClient: {client}")
        for project, data in projects.items():
            print(f"  Project: {project}")
            for repo_type, branches in data["repositories"].items():
                print(f"    Repository: {repo_type}")
                for branch in branches:
                    print(f"      Branch: {branch['branch']}")
                    print(f"      Status: {branch['status'].splitlines()[0]}")  # Show only the first line of the status

def create_directories(client, project, repo_type, branch, base_path):
    """Creates the directory structure for the project."""
    project_path = os.path.join(base_path, client, project, "repositories", repo_type, branch + ".git")

    try:
        os.makedirs(project_path, exist_ok=True)
        print(f"Directory structure created at: {project_path}")
        return project_path
    except OSError as e:
        print(f"Error creating directory structure: {e}")
        return None

def initialize_git_repository(project_path):
    """Initializes a bare Git repository at the specified path."""
    try:
        repo = git.Repo.init(project_path, bare=True)
        print(f"Bare Git repository initialized at: {project_path}")
        return repo
    except git.exc.GitError as e:
        print(f"Error initializing bare Git repository: {e}")
        return None

def get_project_data():
    """Gets project data from the user."""
    client = input("Enter the client name: ")
    project = input("Enter the project name: ")
    while True:
        try:
            repo_type_num = int(input("Choose the repository type (1-backend, 2-frontend, 3-docs, 4-config): "))
            repo_types = ["backend", "frontend", "docs", "config"]
            if 1 <= repo_type_num <= len(repo_types):
                repo_type = repo_types[repo_type_num - 1]
                break
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Enter a number.")
    branch = input("Enter the branch name: ")
    return client, project, repo_type, branch

def create_tree(structure):
    """Creates a tree for clearer visualization."""
    tree = Tree()
    tree.create_node("Clients", "root")

    for client, projects in structure.items():
        tree.create_node(client, client, parent="root")
        for project, data in projects.items():
            tree.create_node(project, project, parent=client)
            for repo_type, branches in data["repositories"].items():
                tree.create_node(repo_type, repo_type, parent=project)
                for branch in branches:
                    tree.create_node(branch['branch'], parent=repo_type)
    return tree

def print_tree(tree, root_id="root", indent=""):
    """Prints the tree recursively."""
    node = tree.get_node(root_id)
    if root_id == "root":
        print(node.tag)
    else:
        print(f"{indent}└── {node.tag}")

    for child_id in node.successors(tree.identifier):
        print_tree(tree, child_id, indent + "    ")

def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Project and Git repository management.")
    parser.add_argument("--client", type=str, help="Client name.")
    parser.add_argument("--project", type=str, help="Project name.")
    parser.add_argument("--list", action="store_true", help="Lists the directory structure.")
    parser.add_argument("--create", action="store_true", help="Creates a new project.")
    parser.add_argument("--branch", type=str, help="Branch name to create or initialize.")
    return parser.parse_args()

def handle_arguments(args, structure):
    """Handles actions based on command-line arguments."""
    if args.list:
        list_structure(structure)
        return

    if args.client:
        client = args.client
        if client not in structure:
            print(f"The client '{client}' does not exist in the structure.")
            return

        if args.project:
            project = args.project
            if project not in structure[client]:
                print(f"The project '{project}' does not exist for the client '{client}'.")
                return

            if args.branch:
                branch = args.branch
                print(f"Creating or initializing the branch '{branch}' for the project '{project}' of client '{client}'.")
                repo_type = "default"  # You can change this as needed
                branch_path = create_directories(client, project, repo_type, branch, base_path)
                if branch_path:
                    initialize_git_repository(branch_path)
            else:
                print(f"Showing details of the project '{project}' for the client '{client}':")
                tree = create_tree({client: {project: structure[client][project]}})
                print_tree(tree)
        else:
            print(f"Showing details of the client '{client}':")
            tree = create_tree({client: structure[client]})
            print_tree(tree)
    elif args.create:
        client, project, repo_type, branch = get_project_data()
        project_path = create_directories(client, project, repo_type, branch, base_path)
        if project_path:
            initialize_git_repository(project_path)
    else:
        print("No valid arguments provided. Use --help to see available options.")

def main():
    """Main function of the script."""
    global base_path
    base_path = "/opt/hexome-systems/projects"  # You can change the base path here
    structure = get_directory_structure(base_path)

    args = parse_arguments()
    if any(vars(args).values()):  # If arguments were passed, handle them
        handle_arguments(args, structure)
    else:
        # Interactive menu if no arguments are passed
        while True:
            print("\nMain Menu:")
            print("1. Show general summary")
            print("2. List directory structure")
            print("3. Select client")
            print("4. Create a new project")
            print("5. Exit")

            option = input("Choose an option (enter the number): ")

            if option == "1":
                show_summary(structure)
                input("\nPress Enter to continue...")
            elif option == "2":
                list_structure(structure)
                input("\nPress Enter to continue...")
            elif option == "3":
                handle_client_option(structure)
            elif option == "4":
                client, project, repo_type, branch = get_project_data()
                project_path = create_directories(client, project, repo_type, branch, base_path)
                if project_path:
                    initialize_git_repository(project_path)
                structure = get_directory_structure(base_path)
                input("\nPress Enter to continue...")
            elif option == "5":
                print("Exiting the script.")
                break
            else:
                print("Invalid option. Please enter a number from the menu.")

if __name__ == "__main__":
    main()
