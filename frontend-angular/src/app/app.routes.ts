import { Routes } from '@angular/router';
import { Home } from './pages/home/home';
import { Search } from './pages/search/search';
import { Domains } from './pages/domains/domains.component';
import { Communities } from './pages/communities/communities.component';
import { LoginComponent } from './pages/auth/login/login.component';
import { RegisterComponent } from './pages/auth/register/register.component';
import { OriginalToolPageComponent } from './pages/tool-detail/original-tool-page/original-tool-page.component';
import { ToolEditComponent } from './pages/tool-edit/tool-edit.component';
import { AboutComponent } from './pages/about/about';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'home', redirectTo: '', pathMatch: 'full' },
  { path: 'search', component: Search },
  { path: 'domains', component: Domains },
  { path: 'communities', component: Communities },
  { path: 'tool/:id', component: OriginalToolPageComponent },
  { path: 'tool-edit/new', component: ToolEditComponent }, // Create new tool
  { path: 'tool-edit/:id', component: ToolEditComponent }, // Edit existing tool
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'about', component: AboutComponent },
  { path: '**', redirectTo: '' } // Wildcard route for 404
];
