import { Routes, RouterModule } from '@angular/router';
import { AuthComponent } from './auth/auth.component';
import { MainPageComponent } from './main-page/main-page.component';
import { RecipeTableComponent } from './recipe-table/recipe-table.component';
import { WidgetComponent } from './widget/widget.component';
import { AuthGuard } from './services/auth.guard';
import { NgModule } from '@angular/core';

export const routes: Routes = [
  { path: 'auth', component: AuthComponent },
  {
    path: 'main-page',
    component: MainPageComponent,
    canActivate: [AuthGuard],
    children: [
      { path: 'app-recipe-table', component: RecipeTableComponent },
      { path: 'widget', component: WidgetComponent },
      //{ path: '', redirectTo: 'app-recipe-table', pathMatch: 'full' }
    ]
  },
  { path: '', redirectTo: '/auth', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
