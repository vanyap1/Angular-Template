import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-widget',
  templateUrl: './widget.component.html',
  styleUrls: ['./widget.component.css'],
  standalone: true,
  imports: [FormsModule]
})
export class WidgetComponent {
  inputText: string = '';
  outputText: string = '';

  constructor(private http: HttpClient, private authService: AuthService) {}

  onButtonClick() {
    const token = this.authService.getToken();
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
    ///?id=${this.inputText}
    this.http.get(`/api/current_user_info/`, { headers, responseType: 'text' })
      .subscribe(
        response => {
          console.log('Response from server:', response);
          this.outputText = response;
        },
        error => {
          console.error('Error occurred:', error);
        }
      );
  }
}
