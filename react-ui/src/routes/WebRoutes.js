import React, { lazy } from 'react';
import { Route, Switch, useLocation } from 'react-router-dom';

// project imports
import Loadable from '../ui-component/Loadable';

// login routing
const HomePage = Loadable(lazy(() => import('../views/web/home')));
const AboutPage = Loadable(lazy(() => import('../views/web/about')));
const MoleculeViewer = Loadable(lazy(() => import('../views/web/MoleculeViewer')));

//-----------------------|| AUTH ROUTING ||-----------------------//

const WebRoutes = () => {
    const location = useLocation();

    return (
        <Switch location={location} key={location.pathname}>
            <Route exact path="/" component={HomePage} />
            <Route exact path="/about" component={AboutPage} />
            <Route exact path="/3d-viewer/:fileName" component={MoleculeViewer} />
        </Switch>
    );
};

export default WebRoutes;
