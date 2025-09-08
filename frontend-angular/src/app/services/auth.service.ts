import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, of } from 'rxjs';
import { tap, catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface User {
  id: number;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  isStaff?: boolean;
  isSuperuser?: boolean;
  dateJoined?: string;
  lastLogin?: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: User;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  firstName?: string;
  lastName?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private baseUrl = environment.apiUrl;
  private tokenKey = 'biotools_token';
  
  // State management
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();
  
  // Signal for reactive programming
  public isAuthenticated = signal<boolean>(false);
  public currentUser = signal<User | null>(null);

  constructor(private http: HttpClient) {
    this.loadUserFromStorage();
  }

  /**
   * Login user with credentials
   */
  login(credentials: LoginCredentials): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.baseUrl}/auth/login/`, credentials)
      .pipe(
        tap(response => {
          this.setSession(response.token, response.user);
        }),
        catchError(error => {
          console.error('Login error:', error);
          throw error;
        })
      );
  }

  /**
   * Register new user
   */
  register(userData: RegisterData): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/auth/register/`, userData)
      .pipe(
        catchError(error => {
          console.error('Registration error:', error);
          throw error;
        })
      );
  }

  /**
   * Logout user
   */
  logout(): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/auth/logout/`, {})
      .pipe(
        tap(() => {
          this.clearSession();
        }),
        catchError(error => {
          console.error('Logout error:', error);
          // Clear session even if logout request fails
          this.clearSession();
          return of(void 0);
        })
      );
  }

  /**
   * Get current user profile
   */
  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/auth/user/`)
      .pipe(
        tap(user => {
          this.currentUserSubject.next(user);
          this.currentUser.set(user);
        }),
        catchError(error => {
          console.error('Get user error:', error);
          this.clearSession();
          throw error;
        })
      );
  }

  /**
   * Update user profile
   */
  updateProfile(userData: Partial<User>): Observable<User> {
    return this.http.patch<User>(`${this.baseUrl}/auth/user/`, userData)
      .pipe(
        tap(user => {
          this.currentUserSubject.next(user);
          this.currentUser.set(user);
        }),
        catchError(error => {
          console.error('Update profile error:', error);
          throw error;
        })
      );
  }

  /**
   * Change password
   */
  changePassword(oldPassword: string, newPassword: string): Observable<void> {
    const data = {
      old_password: oldPassword,
      new_password: newPassword
    };
    
    return this.http.post<void>(`${this.baseUrl}/auth/change-password/`, data)
      .pipe(
        catchError(error => {
          console.error('Change password error:', error);
          throw error;
        })
      );
  }

  /**
   * Request password reset
   */
  requestPasswordReset(email: string): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/auth/password-reset/`, { email })
      .pipe(
        catchError(error => {
          console.error('Password reset request error:', error);
          throw error;
        })
      );
  }

  /**
   * Confirm password reset
   */
  confirmPasswordReset(token: string, newPassword: string): Observable<void> {
    const data = {
      token,
      new_password: newPassword
    };
    
    return this.http.post<void>(`${this.baseUrl}/auth/password-reset-confirm/`, data)
      .pipe(
        catchError(error => {
          console.error('Password reset confirm error:', error);
          throw error;
        })
      );
  }

  /**
   * Verify email address
   */
  verifyEmail(token: string): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/auth/verify-email/`, { token })
      .pipe(
        catchError(error => {
          console.error('Email verification error:', error);
          throw error;
        })
      );
  }

  /**
   * Check if user is authenticated
   */
  isLoggedIn(): boolean {
    return this.isAuthenticated();
  }

  /**
   * Get authentication token
   */
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  /**
   * Get current user value
   */
  getCurrentUserValue(): User | null {
    return this.currentUser();
  }

  /**
   * Set authentication session
   */
  private setSession(token: string, user: User): void {
    localStorage.setItem(this.tokenKey, token);
    this.currentUserSubject.next(user);
    this.currentUser.set(user);
    this.isAuthenticated.set(true);
  }

  /**
   * Clear authentication session
   */
  private clearSession(): void {
    localStorage.removeItem(this.tokenKey);
    this.currentUserSubject.next(null);
    this.currentUser.set(null);
    this.isAuthenticated.set(false);
  }

  /**
   * Load user from storage on service initialization
   */
  private loadUserFromStorage(): void {
    const token = this.getToken();
    if (token) {
      // Verify token is still valid by getting current user
      this.getCurrentUser().subscribe({
        next: () => {
          // User loaded successfully, authentication state already set
        },
        error: () => {
          // Token is invalid, clear session
          this.clearSession();
        }
      });
    }
  }
}
