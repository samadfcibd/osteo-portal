// assets
import { IconBrandChrome, IconHelp, IconSitemap, IconGrowth } from '@tabler/icons';

// constant
const icons = {
    IconBrandChrome: IconBrandChrome,
    IconHelp: IconHelp,
    IconSitemap: IconSitemap,
    IconGrowth: IconGrowth,
};

//-----------------------|| SAMPLE PAGE & DOCUMENTATION MENU ITEMS ||-----------------------//

export const other = {
    id: 'sample-docs-roadmap',
    type: 'group',
    children: [
        {
            id: 'organism-upload',
            title: 'Organisms Upload',
            type: 'item',
            url: '/organism-upload',
            icon: icons['IconGrowth'],
            breadcrumbs: false
        },
        {
            id: 'pdb-upload',
            title: 'PDB Upload',
            type: 'item',
            url: '/pdb-upload',
            icon: icons['IconGrowth'],
            breadcrumbs: false
        },
        // {
        //     id: 'sample-page',
        //     title: 'Sample Page',
        //     type: 'item',
        //     url: '/sample-page',
        //     icon: icons['IconBrandChrome'],
        //     breadcrumbs: false
        // },
        // {
        //     id: 'documentation',
        //     title: 'Documentation',
        //     type: 'item',
        //     url: 'https://docs.appseed.us/products/react/flask-berry-dashboard',
        //     icon: icons['IconHelp'],
        //     external: true,
        //     target: true
        // }
    ]
};
