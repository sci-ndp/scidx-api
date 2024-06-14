# Standard Branch Naming Convention for GitHub

Establishing a standard naming convention for branches in a GitHub project is crucial for maintaining organization and facilitating an understanding of each branch's purpose among team members. While there is no one-size-fits-all approach, there are common practices that many teams adopt to create an effective standard. Here's a recommended structure you can adjust according to your project's needs:

## General Structure

```
[type]/[descriptive-name]
```

## Common Types of Branches

- **feat**: For new features or significant additions to your project.
- **fix**: For bug fixes.
- **docs**: For changes to documentation.
- **style**: For changes that do not affect the meaning of the code (space, formatting, etc.).
- **refactor**: For code changes that neither fix a bug nor add a feature.
- **test**: For adding or correcting tests.
- **chore**: For updates and maintenance tasks without source code changes.

## Examples

- `feat/login-social-media`: Indicates the development of a new feature related to social media login.
- `fix/bug-login`: Refers to the correction of a specific bug in the login system.
- `docs/update-readme`: For updates or improvements to the project's README file.
- `refactor/cleanup-code-login`: Implies a restructuring of the login code, without changing its functionality.

## Tips for Branch Names

1. **Be brief but descriptive**: Names should be descriptive enough that anyone on the team can understand the purpose of the branch just by looking at its name, but not so long that they are hard to read or handle.
2. **Use dashes to separate words**: This enhances the readability of the branch name.
3. **Avoid special characters**: Keep the branch names simple and avoid using special characters or spaces.
4. **Prefix with the type of task**: Helps to quickly categorize branches and facilitates the search for branches related to specific tasks.
5. **Include task/ticket identifiers**: If your team uses a task or ticket tracking system, consider including the ticket identifier in the branch name for quick reference.

Return to [Contributing](contributing.md)
