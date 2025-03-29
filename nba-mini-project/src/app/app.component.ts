import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TabsComponent } from './tabs/tabs.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, TabsComponent],
  template: `
    <app-tabs></app-tabs>
    <router-outlet></router-outlet>
  `
})
export class AppComponent {}