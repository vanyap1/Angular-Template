import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private token: string | null = null;

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<any> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });

    const body = new HttpParams()
      .set('username', username)
      .set('password', password);

    return this.http.post('/api/token', body.toString(), { headers }).pipe(
      tap((response: any) => {
        this.token = response.access_token;
        if (this.isBrowser()) {
          localStorage.setItem('token', response.access_token);
        }
      })
    );
  }

  getToken(): string | null {
    if (this.isBrowser()) {
      return this.token || localStorage.getItem('token');
    }
    return this.token;
  }

  getAuthHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Authorization': `Bearer ${this.getToken()}`
    });
  }

  logout() {
    this.token = null;
    if (this.isBrowser()) {
      localStorage.removeItem('token');
    }
  }

  private isBrowser(): boolean {
    return typeof window !== 'undefined' && typeof window.document !== 'undefined';
  }
}
