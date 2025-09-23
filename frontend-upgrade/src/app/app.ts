import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { PageFooter } from './components/page-footer/page-footer';
import { Navigation } from './components/navigation/navigation';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Navigation, PageFooter],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('bio.tools');
}
