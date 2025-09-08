import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Header } from './components/header/header';
import { PageFooter } from './components/page-footer/page-footer';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Header, PageFooter],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('frontend-upgrade');
}
