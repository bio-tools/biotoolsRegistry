# Bio.tools Frontend (Angular)

This is a modern Angular 20 application for the bio.tools registry, providing a clean and responsive interface for discovering bioinformatics tools and services.

## Features

### ✅ Currently Implemented
- **Modern Angular 20 with Standalone Components**
- **Angular Material UI** for consistent design
- **Responsive Navigation Bar** with search functionality
- **Home Page** with hero section and feature highlights
- **Search Page** with filtering and pagination
- **TypeScript Models** for bio.tools data structures
- **API Service** ready for bio.tools backend integration
- **Mock Data** for development and testing

### 🚧 Next Steps
- Connect to real bio.tools API
- Implement tool detail pages
- Add user authentication
- Add tool registration/editing
- Implement domains and communities pages
- Add advanced filtering
- Mobile optimization

## Project Structure

```
src/app/
├── components/          # Reusable UI components
│   ├── navigation/      # Main navigation bar
│   └── search-bar/      # Search input component
├── pages/              # Route components (pages)
│   ├── home/           # Homepage
│   └── search/         # Search results page
├── models/             # TypeScript interfaces
│   ├── tool.model.ts   # Tool data structure
│   └── search.model.ts # Search-related models
├── services/           # API and business logic
│   └── biotools-api.service.ts
└── app.* files         # Root application files
```

## Technologies Used

- **Angular 20** - Latest Angular framework
- **Angular Material** - Material Design components
- **TypeScript** - Type-safe JavaScript
- **SCSS** - Enhanced CSS with variables and nesting
- **RxJS** - Reactive programming with observables

## Development Setup

### Prerequisites
- Node.js 18+ and npm
- Angular CLI (`npm install -g @angular/cli`)

### Installation
```bash
# Install dependencies
npm install

# Start development server
ng serve

# Open browser at http://localhost:4200
```

### Development Commands
```bash
# Generate new component
ng generate component components/component-name

# Generate new service
ng generate service services/service-name

# Build for production
ng build

# Run tests
ng test

# Run linting
ng lint
```

## API Integration

The application is designed to work with the bio.tools API:

### Current Mock Data
The `BiotoolsApiService` currently uses mock data for development. To switch to the real API:

1. Update the `baseUrl` in `biotools-api.service.ts`
2. Replace `getMockTools()` calls with `searchTools()`
3. Handle authentication if required

### API Endpoints Used
- `GET /api/tool` - Search tools
- `GET /api/tool/{id}` - Get specific tool
- `GET /api/tool/facets` - Get search facets
- `GET /api/stats` - Get registry statistics

## Migration from AngularJS

This application replaces the legacy AngularJS frontend with:

### Improvements
- **Performance**: Faster rendering and smaller bundle sizes
- **Maintainability**: TypeScript and modern development tools
- **Security**: Latest security updates and best practices
- **Mobile-First**: Responsive design from the ground up
- **Accessibility**: Better screen reader and keyboard support

### Architecture Changes
- **Standalone Components** instead of modules
- **Signals** for reactive state management
- **Modern RxJS** patterns for async operations
- **Angular Material** instead of Bootstrap
- **TypeScript** throughout the application

## Deployment

### Production Build
```bash
ng build --configuration production
```

### Docker (Optional)
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist/ ./dist/
EXPOSE 4200
CMD ["npx", "http-server", "dist", "-p", "4200"]
```

## Contributing

1. Follow Angular style guide
2. Use TypeScript strictly
3. Add tests for new components
4. Update this README for new features

## Migration Progress

- ✅ Project setup and configuration
- ✅ Navigation component
- ✅ Search functionality
- ✅ Home page
- ✅ Basic tool listing
- 🚧 API integration
- 🔲 Tool detail pages
- 🔲 User authentication
- 🔲 Tool registration
- 🔲 Advanced search features
- 🔲 Mobile optimization
