import { Component } from '@angular/core';
import { MatButton, MatIconButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { NavigationEnd, Router, RouterLink, RouterLinkActive } from '@angular/router';
import { SearchBar } from '../search-bar/search-bar';

@Component({
  selector: 'app-navigation',
  imports: [
    SearchBar,
    MatButton,
    MatIcon,
    MatIconButton,
    RouterLink,
    RouterLinkActive
  ],
  templateUrl: './navigation.html',
  styleUrl: './navigation.scss'
})
export class Navigation {

  isHomePage = false;

  constructor(private router: Router) {
    const path = this.router.url.split('?')[0].split('#')[0];
    this.isHomePage = path === '/';

    this.router.events.subscribe(e => {
      if (e instanceof NavigationEnd) {
        const path = this.router.url.split('?')[0].split('#')[0];
        this.isHomePage = path === '/';
      }
    });
  }
}
