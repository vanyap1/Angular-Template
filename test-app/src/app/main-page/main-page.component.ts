import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterOutlet, NavigationEnd } from '@angular/router';
import { UserListEditor } from '../userEditor/userEditor.component';
import { WidgetComponent } from '../widget/widget.component';
import { AuthService } from '../services/auth.service';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { filter } from 'rxjs/operators';
import { BoilerSchedulerComponent } from '../boiler-scheduler/boiler-scheduler.component';
import { SensorDashboardComponent } from '../sensor-dashboard/sensor-dashboard.component';
import { WebcamStreamComponent } from '../webcam/webcam-stream.component';

@Component({
  selector: 'app-main-page',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    UserListEditor,
    WidgetComponent,
    SidebarComponent,
    BoilerSchedulerComponent,
    SensorDashboardComponent,
    WebcamStreamComponent
  ],
  templateUrl: './main-page.component.html',
  styleUrls: ['./main-page.component.css']
})
export class MainPageComponent implements OnInit {
  currentRoute: string = '';

  constructor(private router: Router, private authService: AuthService) {}

  ngOnInit() {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: NavigationEnd) => {
      this.currentRoute = event.urlAfterRedirects;
    });
  }

  navigateTo(page: string) {
    this.router.navigate([`/${page}`]);
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/auth']);
  }
}
