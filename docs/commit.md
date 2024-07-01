# Effective Commit Messages Guide

Writing clear and concise commit messages is crucial for maintaining a readable and understandable history in your project. This guide provides recommendations for writing effective commit messages within a 50-character limit.

## Structure of a Good Commit Message

A good commit message should answer two questions: what changed and why. However, given the 50-character limit, focus on the "what" and imply the "why" when possible.

```
[type]: Short Change Description or Issue Number
```

## Types of Changes

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **test**: Adding missing tests or correcting existing tests
- **wip**: Work in progress (unfinished changes)

## Examples

- `feat: Add login API`
- `fix: Resolve login redirect`
- `fix: #23`
- `docs: Update README`
- `style: Format with Prettier`
- `refactor: Simplify login check`
- `test: Cover edge cases`
- `wip: implement feature topics list (#123)`

## Tips for Writing Concise Commit Messages

1. **Start with a Capital Letter**: Begin your message with a capital letter to maintain consistency.
2. **Use Present Tense**: Write your commit message in present tense, "Add feature" not "Added feature".
3. **No Period at the End**: Skip the period at the end of the message to save space and maintain formatting.
4. **Use Imperative Mood**: Frame your message as a command or instruction, "Fix bug" not "Fixes bug".
5. **Be Specific**: Use specific terms that directly reflect the changes made.

Remember, the goal of a commit message is to clearly and succinctly convey the essence of your change.

Return to [Contributing](contributing.md).
