import { Routes, RouterModule } from '@angular/router';
import { TabsComponent } from './tabs/tabs.component';
import { NewsListComponent } from './news-list/news-list.component';

export const routes: Routes = [
    {path: 'news', component: NewsListComponent},
    { path: '', redirectTo: 'news', pathMatch: 'full' }, // 默认路由
    { path: '**', redirectTo: 'news' } // 通配符路由
];
