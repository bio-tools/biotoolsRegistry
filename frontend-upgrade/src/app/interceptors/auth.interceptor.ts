import { HttpRequest, HttpHandlerFn, HttpEvent, HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth/auth.service';
import { Router } from '@angular/router';

export const AuthInterceptor: HttpInterceptorFn = (
  request: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Get the auth token from the service
  const authToken = authService.getToken();

  // Clone the request and add the authorization header if we have a token
  if (authToken) {
    request = request.clone({
      setHeaders: {
        Authorization: `Token ${authToken}`
      }
    });
  }

  // Handle the request and catch any auth errors
  return next(request).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        // Token is invalid or expired, logout and redirect to login
        authService.logout().subscribe();
        router.navigate(['/login']);
      }
      return throwError(() => error);
    })
  );
};