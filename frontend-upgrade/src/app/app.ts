import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Header } from './components/header/header';
import { Home } from './pages/home/home';
import { PageFooter } from './components/page-footer/page-footer';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Header, Home, PageFooter],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('frontend-upgrade');
}
