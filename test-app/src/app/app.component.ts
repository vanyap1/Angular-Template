import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { WidgetComponent } from './widget/widget.component';
import { HttpClientModule } from '@angular/common/http'; // Додайте цей імпорт

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, WidgetComponent, HttpClientModule], // Додайте HttpClientModule до імпортів
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  title = 'test-app';

  navigateTo(page: string) {
    // Логіка навігації, наприклад, використання Router для переходу на інші сторінки
    console.log(`Navigating to ${page}`);
  }
}