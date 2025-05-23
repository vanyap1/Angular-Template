import { Component, ViewChild, AfterViewInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { RecipeTableComponent } from './recipe-table/recipe-table.component';
import { AuthComponent } from './auth/auth.component';
import { WidgetComponent } from './widget/widget.component';
import { MainPageComponent } from './main-page/main-page.component';

import { NotificationComponent } from './shared/notification/notification.component';
import { NotificationService } from './services/notification.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RecipeTableComponent, AuthComponent, WidgetComponent, MainPageComponent, NotificationComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements AfterViewInit {
  title = 'test-app';

  @ViewChild(NotificationComponent) notification!: NotificationComponent;

  constructor(private notificationService: NotificationService) {}

  ngAfterViewInit() {
    this.notificationService.register(this.notification);
  }

  navigateTo(page: string) {
    console.log(`Navigating to ${page}`);
  }
}
