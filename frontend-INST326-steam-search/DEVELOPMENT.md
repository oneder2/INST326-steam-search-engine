# Frontend Development Guide

This document provides comprehensive development guidelines for the **Steam Game Search Engine Frontend** service in the monorepo, including setup instructions, coding standards, and best practices.

## 🏗️ Monorepo Context

This frontend service is part of a **monorepo architecture**:

```
INST326-steam-searcher-engine/
├── frontend-INST326-steam-search/    # This service (Next.js)
├── backend-INST326-steam-search/     # Backend API (FastAPI)
├── docs/                               # Shared documentation
└── README.md                           # Main project documentation
```

## 🛠️ Development Environment Setup

### Prerequisites

Ensure you have the following installed:

- **Node.js** 18.0.0 or higher
- **Python** 3.8+ (for backend service)
- **npm** 8.0.0 or higher
- **Git** for version control
- **VS Code** (recommended) with the following extensions:
  - TypeScript and JavaScript Language Features
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense
  - Auto Rename Tag
  - Python (for backend development)

### Initial Setup

1. **Clone the monorepo and navigate to frontend**
   ```bash
   git clone https://github.com/oneder2/INST326-steam-searcher-engine.git
   cd INST326-steam-searcher-engine/frontend-INST326-steam-search
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Environment configuration**
   ```bash
   cp .env.local.example .env.local
   ```

   Edit `.env.local` with your configuration:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   NEXT_PUBLIC_APP_URL=http://localhost:3000
   NEXT_PUBLIC_DEBUG=true
   ```

4. **Setup backend service (required for full functionality)**
   ```bash
   # In a separate terminal
   cd ../backend-INST326-steam-search
   pip install -r requirements-core.txt
   python main.py
   ```

5. **Start frontend development server**
   ```bash
   # Back in frontend directory
   npm run dev
   ```

6. **Alternative: Start both services simultaneously**
   ```bash
   # Install concurrently if not already installed
   npm install

   # Start both frontend and backend
   npm run monorepo:dev
   ```

7. **Verify setup**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
   - Verify TypeScript compilation with `npm run type-check`

## 📁 Frontend Project Structure

### Monorepo Context

```
INST326-steam-searcher-engine/           # Monorepo root
├── frontend-INST326-steam-search/     # This frontend service
│   ├── src/                            # Frontend source code
│   ├── docs/                           # Frontend-specific docs
│   ├── test/                           # Frontend tests
│   ├── package.json                    # Frontend dependencies
│   ├── DEVELOPMENT.md                  # This file
│   └── DEPLOYMENT.md                   # Frontend deployment guide
├── backend-INST326-steam-search/     # Backend API service
├── docs/                               # Shared project documentation
└── README.md                           # Main project documentation
```

### Frontend Directory Organization

```
frontend-INST326-steam-search/
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── Layout/          # Layout components (headers, footers)
│   │   ├── Search/          # Search-related components
│   │   ├── FunctionLibrary/ # Function documentation components
│   │   └── Common/          # Shared utility components
│   ├── pages/               # Next.js pages and API routes
│   │   ├── api/             # Next.js API routes (proxy to backend)
│   │   ├── function-library.tsx # Function library page
│   │   └── ...              # Other pages
│   ├── services/            # Backend API integrations
│   ├── types/               # TypeScript type definitions
│   ├── constants/           # Application constants
│   ├── hooks/               # Custom React hooks
│   ├── utils/               # Pure utility functions
│   └── styles/              # Global styles and CSS
├── test/                    # Frontend-specific tests
├── docs/                    # Frontend documentation
└── public/                  # Static assets
```

### File Naming Conventions

- **Components**: PascalCase (e.g., `SearchBox.tsx`)
- **Pages**: kebab-case (e.g., `function-library.tsx`)
- **Utilities**: camelCase (e.g., `formatPrice.ts`)
- **Types**: PascalCase (e.g., `ApiTypes.ts`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_ENDPOINTS.ts`)

## 🎨 Coding Standards

### TypeScript Guidelines

1. **Always use TypeScript** for new files
2. **Define interfaces** for all data structures
3. **Use strict type checking** - avoid `any` type
4. **Export types** from dedicated type files
5. **Use generic types** where appropriate

Example:
```typescript
// Good
interface SearchResult {
  id: number;
  title: string;
  score: number;
}

const processResults = (results: SearchResult[]): SearchResult[] => {
  return results.filter(result => result.score > 0.5);
};

// Avoid
const processResults = (results: any) => {
  return results.filter((result: any) => result.score > 0.5);
};
```

### React Component Guidelines

1. **Use functional components** with hooks
2. **Define prop interfaces** for all components
3. **Use default props** when appropriate
4. **Implement proper error boundaries**
5. **Follow the single responsibility principle**

Example:
```typescript
interface SearchBoxProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export default function SearchBox({
  value,
  onChange,
  placeholder = "Search...",
  disabled = false
}: SearchBoxProps) {
  // Component implementation
}
```

### CSS and Styling

1. **Use Tailwind CSS** for styling
2. **Create custom CSS classes** for complex components
3. **Follow mobile-first** responsive design
4. **Use CSS variables** for theme colors
5. **Maintain consistent spacing** using Tailwind scale

Example:
```typescript
// Good - Tailwind classes
<div className="bg-steam-blue border border-steam-blue-light rounded-steam p-6">

// Good - Custom component class
<div className="card-steam">

// Avoid - Inline styles
<div style={{ backgroundColor: '#1b2838', padding: '24px' }}>
```

## 🧪 Testing Guidelines

### Unit Testing

1. **Test all utility functions**
2. **Test component behavior**, not implementation
3. **Mock external dependencies**
4. **Use descriptive test names**
5. **Follow AAA pattern** (Arrange, Act, Assert)

Example:
```typescript
describe('validateSearchQuery', () => {
  it('should return valid result for clean input', () => {
    // Arrange
    const input = 'roguelike games';
    
    // Act
    const result = validateSearchQuery(input);
    
    // Assert
    expect(result.isValid).toBe(true);
    expect(result.cleanQuery).toBe('roguelike games');
    expect(result.errors).toHaveLength(0);
  });
});
```

### Component Testing

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import SearchBox from '@/components/Search/SearchBox';

describe('SearchBox', () => {
  it('should call onChange when input value changes', () => {
    const mockOnChange = jest.fn();
    render(<SearchBox value="" onChange={mockOnChange} />);
    
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'test' } });
    
    expect(mockOnChange).toHaveBeenCalledWith('test');
  });
});
```

## 📝 Documentation Standards

### Code Comments

1. **Write JSDoc comments** for all public functions
2. **Explain complex algorithms** with inline comments
3. **Document component props** and behavior
4. **Include usage examples** in comments
5. **Keep comments up-to-date** with code changes

Example:
```typescript
/**
 * Calculates fusion ranking score combining multiple relevance signals
 * 
 * @param bm25Score - BM25 keyword relevance score (0.0 - 1.0)
 * @param semanticScore - Semantic similarity score (0.0 - 1.0)
 * @param qualityMetrics - Game quality metrics
 * @returns Final ranking score (0.0 - 1.0)
 * 
 * @example
 * const score = calculateFusionRanking(0.8, 0.7, { review_stability: 0.9 });
 */
function calculateFusionRanking(
  bm25Score: number,
  semanticScore: number,
  qualityMetrics: RankingMetrics
): number {
  // Implementation with inline comments for complex logic
}
```

### Function Library Documentation

All functions should be documented in the function library:

1. **Create markdown files** in `docs/functions/`
2. **Follow the standard format** (see existing examples)
3. **Include working code examples**
4. **Update documentation** when functions change
5. **Add appropriate tags** for searchability

## 🔧 Development Workflow

### Git Workflow

1. **Create feature branches** from `main`
2. **Use descriptive commit messages**
3. **Keep commits atomic** and focused
4. **Rebase before merging** to maintain clean history
5. **Delete merged branches**

Commit message format:
```
type(scope): description

feat(search): add semantic search functionality
fix(api): handle network timeout errors
docs(readme): update installation instructions
style(components): fix linting issues
```

### Code Review Process

1. **Create pull requests** for all changes
2. **Request reviews** from team members
3. **Address feedback** promptly
4. **Ensure CI passes** before merging
5. **Update documentation** as needed

### Development Commands

#### Frontend-Only Commands
```bash
# Development
npm run dev              # Start frontend development server
npm run type-check       # Check TypeScript types
npm run lint             # Run ESLint
npm run lint:fix         # Fix auto-fixable issues

# Testing
npm test                 # Run frontend tests
npm run test:watch       # Run tests in watch mode
npm run test:coverage    # Generate coverage report

# Building
npm run build            # Create production build
npm run start            # Start production server
```

#### Monorepo Commands (Frontend + Backend)
```bash
# Install dependencies for both services
npm run monorepo:install

# Start both frontend and backend simultaneously
npm run monorepo:dev

# Start backend only (from frontend directory)
npm run monorepo:backend
```

#### Backend Commands (from backend directory)
```bash
cd ../backend-INST326-steam-search

# Start backend development server
python main.py
# OR
uvicorn main:app --reload

# Install backend dependencies
pip install -r requirements-core.txt
```

## 🐛 Debugging

### Common Issues

1. **TypeScript errors**: Run `npm run type-check` to see all type issues
2. **Import errors**: Check file paths and ensure exports are correct
3. **Styling issues**: Verify Tailwind classes and check for typos
4. **API errors**: Check network tab and API endpoint configuration

### Debugging Tools

1. **React Developer Tools** - Browser extension for React debugging
2. **Redux DevTools** - If using Redux for state management
3. **VS Code Debugger** - Set breakpoints in VS Code
4. **Console logging** - Use structured logging for debugging

Example debugging setup:
```typescript
// Use structured logging
console.log('Search query:', { query, filters, timestamp: Date.now() });

// Add debug information in development
if (process.env.NODE_ENV === 'development') {
  console.debug('Component rendered with props:', props);
}
```

## 🚀 Performance Guidelines

### Frontend Performance

1. **Use React.memo** for expensive components
2. **Implement proper loading states**
3. **Optimize images** with Next.js Image component
4. **Use code splitting** for large components
5. **Minimize bundle size** by avoiding unnecessary dependencies

### API Performance

1. **Implement request caching**
2. **Use debouncing** for search inputs
3. **Paginate large result sets**
4. **Handle loading and error states**
5. **Optimize API response sizes**

## 🔒 Security Considerations

1. **Validate all user inputs** on both client and server
2. **Sanitize data** before displaying to users
3. **Use HTTPS** in production
4. **Implement proper error handling** without exposing sensitive information
5. **Keep dependencies updated** to avoid security vulnerabilities

## 📦 Deployment

### Production Checklist

- [ ] All tests pass
- [ ] TypeScript compilation succeeds
- [ ] No ESLint errors
- [ ] Environment variables configured
- [ ] Build succeeds without warnings
- [ ] Performance metrics acceptable
- [ ] Security scan completed

### Environment Configuration

```env
# Production environment variables
NODE_ENV=production
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com
NEXT_PUBLIC_APP_URL=https://yourdomain.com
NEXT_PUBLIC_GA_ID=your-analytics-id
```

## 🤝 Team Collaboration

### Monorepo Workflow

1. **Service Independence**: Frontend and backend can be developed independently
2. **Shared Documentation**: Use `docs/` for project-wide documentation
3. **Cross-Service Communication**: Frontend communicates with backend via API
4. **Coordinated Deployment**: Each service deploys independently but should be compatible

### Communication

1. **Use descriptive commit messages** with service prefixes:
   ```
   frontend: add new search component
   backend: implement health check endpoint
   docs: update API documentation
   ```
2. **Document decisions** in code comments and shared docs
3. **Share knowledge** through code reviews
4. **Ask questions** when uncertain about cross-service integration
5. **Update documentation** when making changes that affect other services

### Code Ownership

1. **Frontend Team**: Responsible for `frontend-INST326-steam-search/`
2. **Backend Team**: Responsible for `backend-INST326-steam-search/`
3. **Shared Responsibility**: Documentation in `docs/`
4. **Cross-Service Reviews**: Review changes that affect API contracts
5. **Integration Testing**: Ensure frontend-backend compatibility

### Development Best Practices

1. **API Contract**: Maintain compatibility when changing API endpoints
2. **Environment Variables**: Keep frontend and backend env vars in sync
3. **Error Handling**: Implement proper error handling for API communication
4. **Testing**: Test both services independently and together
5. **Documentation**: Update both service-specific and shared documentation

---

This development guide should be updated as the monorepo evolves. For questions or suggestions, please discuss with the team during development sessions.

## 📚 Related Documentation

- [Main Project README](../../README.md) - Monorepo overview
- [Backend Documentation](../backend-INST326-steam-search/README.md) - Backend API guide
- [Deployment Guide](DEPLOYMENT.md) - Frontend deployment instructions
- [Shared Documentation](../../docs/) - Project-wide documentation
