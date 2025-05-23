import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { RecipeTableComponent } from './recipe-table/recipe-table.component';
import { AuthComponent } from './auth/auth.component';
import { WidgetComponent } from './widget/widget.component';
import { MainPageComponent } from './main-page/main-page.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RecipeTableComponent, AuthComponent, WidgetComponent, MainPageComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  title = 'test-app';

  navigateTo(page: string) {
    console.log(`Navigating to ${page}`);
  }
}
