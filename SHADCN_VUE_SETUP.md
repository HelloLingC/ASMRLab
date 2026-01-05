# shadcn-vue Setup

This project has been configured to use [shadcn-vue](https://www.shadcn-vue.com/), a collection of reusable Vue components built with Radix Vue and Tailwind CSS.

## Installation

All required dependencies have been installed:

- `radix-vue` - Accessible component primitives
- `class-variance-authority` - For component variants
- `clsx` - For conditional class names
- `tailwind-merge` - For merging Tailwind classes
- `@vueuse/core` - Vue composition utilities

## Configuration

### Files Created/Modified

1. **`components.json`** - Configuration file for shadcn-vue
2. **`src/lib/utils.js`** - Utility function `cn()` for merging classes
3. **`src/components/ui/`** - Directory containing shadcn-vue components
4. **`tailwind.config.js`** - Updated with shadcn-vue color system
5. **`src/assets/main.css`** - Added shadcn-vue CSS variables

## Available Components

The following components are available in `src/components/ui/`:

- **Button** - Button component with multiple variants
- **Card** - Card container with header, content, footer
- **Input** - Form input component
- **Label** - Form label component
- **Badge** - Badge component for labels
- **Alert** - Alert component for notifications

## Usage Example

### Importing Components

```vue
<script setup>
import { Button, Card, CardHeader, CardTitle, CardContent } from '@/components/ui'
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Hello World</CardTitle>
    </CardHeader>
    <CardContent>
      <Button variant="default">Click me</Button>
    </CardContent>
  </Card>
</template>
```

### Button Variants

```vue
<Button variant="default">Default</Button>
<Button variant="destructive">Destructive</Button>
<Button variant="outline">Outline</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>
```

### Button Sizes

```vue
<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>
<Button size="icon">Icon</Button>
```

### Card Example

```vue
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description goes here</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

### Alert Example

```vue
<Alert variant="default">
  <AlertTitle>Heads up!</AlertTitle>
  <AlertDescription>
    This is an alert message.
  </AlertDescription>
</Alert>

<Alert variant="destructive">
  <AlertTitle>Error</AlertTitle>
  <AlertDescription>
    Something went wrong.
  </AlertDescription>
</Alert>
```

## Adding More Components

To add more shadcn-vue components:

1. Visit the [shadcn-vue documentation](https://www.shadcn-vue.com/)
2. Copy the component code
3. Place it in `src/components/ui/`
4. Export it from `src/components/ui/index.js`

## Customization

You can customize the theme by modifying:

- **Colors**: Update CSS variables in `src/assets/main.css` under the `@theme` block
- **Components**: Modify component files in `src/components/ui/`
- **Tailwind Config**: Update `tailwind.config.js` for additional theme customization

## Utility Function

The `cn()` utility function is available for merging Tailwind classes:

```vue
<script setup>
import { cn } from '@/lib/utils'
</script>

<template>
  <div :class="cn('base-class', condition && 'conditional-class')">
    Content
  </div>
</template>
```

## Resources

- [shadcn-vue Documentation](https://www.shadcn-vue.com/)
- [Radix Vue Documentation](https://www.radix-vue.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)

