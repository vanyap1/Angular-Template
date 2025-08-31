import { Routes, RouterModule } from '@angular/router';
import { AuthComponent } from './auth/auth.component';
import { MainPageComponent } from './main-page/main-page.component';
import { UserListEditor } from './userEditor/userEditor.component';
import { WidgetComponent } from './widget/widget.component';
import { AuthGuard } from './services/auth.guard';
import { NgModule } from '@angular/core';
import { BoilerSchedulerComponent } from './boiler-scheduler/boiler-scheduler.component';
import { SensorDashboardComponent } from './sensor-dashboard/sensor-dashboard.component';
import { WebcamStreamComponent } from './webcam/webcam-stream.component';
export const routes: Routes = [
  { path: 'auth', component: AuthComponent },
  {
    path: 'main-page',
    component: MainPageComponent,
    canActivate: [AuthGuard],
    children: [
      { path: 'app-userEditor', component: UserListEditor },
      { path: 'boiler-scheduler', component: BoilerSchedulerComponent },
      { path: 'widget', component: WidgetComponent },
      { path: 'sensor-dashboard', component: SensorDashboardComponent },
      { path: 'webcam', component: WebcamStreamComponent },
      //{ path: '', redirectTo: 'app-userEditor', pathMatch: 'full' }
    ]
  },
  { path: '', redirectTo: '/auth', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
