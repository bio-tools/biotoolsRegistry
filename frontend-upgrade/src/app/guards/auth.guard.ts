import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService } from '../services/auth/auth.service';

export const AuthGuard: CanActivateFn = (route, state) => {
    const authService = inject(AuthService);

    if (authService.isLoggedIn()) {
        return true;
    } else {
        const router = inject(Router);
        return router.createUrlTree(['/login']);
    }
};
