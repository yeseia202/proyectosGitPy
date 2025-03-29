#!/usr/bin/env python3
import os
import git
import argparse
from treelib import Node, Tree

# Configura explícitamente el ejecutable de Git si no está en el PATH
git.Git.refresh(path="/usr/bin/git")  # Cambia la ruta si es necesario

# Existing functions (not shown here for brevity)

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
                branch_path = create_directories(client, project, repo_type, branch)
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
        project_path = create_directories(client, project, repo_type, branch)
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
                project_path = create_directories(client, project, repo_type, branch)
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
