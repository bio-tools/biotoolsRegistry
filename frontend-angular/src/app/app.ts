import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Navigation } from './components/navigation/navigation';
import { PageFooter } from './components/page-footer/page-footer.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, Navigation, PageFooter],
  template: `
    <app-navigation></app-navigation>
    <main>
      <router-outlet></router-outlet>
    </main>
    <app-page-footer></app-page-footer>
  `,
  styleUrl: './app.scss'
})
export class App {
  title = signal('bio.tools - Bioinformatics Tools Registry');
}
