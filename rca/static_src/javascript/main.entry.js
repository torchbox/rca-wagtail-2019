import '@babel/polyfill';
import Alpine from 'alpinejs';

import Accordion from './components/accordion';
import ActualHeight from './components/actual-height';
import AnchorNav from './components/anchor-nav';
import BackLink from './components/back-link';
import Carousel from './components/carousel';
import PeekFullCarousel from './components/carousel-full-peek';
import PeekCarousel from './components/carousel-peek';
import EmailShare from './components/email-share';
import EventToggleSwitch from './components/event-toggle-switch';
import FormFocus from './components/form-focus';
import GridSizeVariables from './components/grid-size-variables';
import HeaderDrawer from './components/header-drawer';
import './components/home-menu';
import './components/lazyload-images';
import MobileSubMenu from './components/mobile-sub-menu';
import './components/modal';
import './components/outdated-banner';
import './components/parallax';
import Sticky from './components/position-sticky-event';
import ProgrammeToggleSwitch from './components/programme-toggle-switch';
import ProjectFilters from './components/project-filters';
import RelatedContent from './components/related-content';
import ScholarshipList from './components/scholarship-list';
import SitewideAlert from './components/sitewide-alert';
import Slideshow from './components/slideshow';
import TableHint from './components/table-hint';
import './components/stats-block';
import './components/sticky-header';
import './components/sticky-point';
import SubMenu from './components/submenu';
import Tabs from './components/tabs';
import VideoModal from './components/video-modal';
import VideoPlayer from './components/video-stream';

import '../sass/main.scss';

document.addEventListener('DOMContentLoaded', () => {
    /* eslint-disable no-new, no-restricted-syntax */

    // GridSizeVariables first to ensure custom properites are populated
    for (const gridVariables of document.querySelectorAll(
        GridSizeVariables.selector(),
    )) {
        new GridSizeVariables(gridVariables);
    }

    for (const sitewideAlert of document.querySelectorAll(
        SitewideAlert.selector(),
    )) {
        new SitewideAlert(sitewideAlert);
    }

    for (const formFocus of document.querySelectorAll(FormFocus.selector())) {
        new FormFocus(formFocus);
    }

    for (const tabs of document.querySelectorAll(Tabs.selector())) {
        new Tabs(tabs);
    }

    for (const accordion of document.querySelectorAll(Accordion.selector())) {
        new Accordion(accordion);
    }

    for (const carousel of document.querySelectorAll(Carousel.selector())) {
        new Carousel(carousel);
    }

    for (const peekcarousel of document.querySelectorAll(
        PeekCarousel.selector(),
    )) {
        new PeekCarousel(peekcarousel);
    }

    for (const peekfullcarousel of document.querySelectorAll(
        PeekFullCarousel.selector(),
    )) {
        new PeekFullCarousel(peekfullcarousel);
    }

    for (const slideshow of document.querySelectorAll(Slideshow.selector())) {
        new Slideshow(slideshow);
    }

    for (const headerdrawer of document.querySelectorAll(
        HeaderDrawer.selector(),
    )) {
        new HeaderDrawer(headerdrawer);
    }

    for (const backlink of document.querySelectorAll(BackLink.selector())) {
        new BackLink(backlink);
    }

    for (const submenu of document.querySelectorAll(SubMenu.selector())) {
        new SubMenu(submenu);
    }

    for (const relatedcontent of document.querySelectorAll(
        RelatedContent.selector(),
    )) {
        new RelatedContent(relatedcontent);
    }

    for (const mobilesubmenu of document.querySelectorAll(
        MobileSubMenu.selector(),
    )) {
        new MobileSubMenu(mobilesubmenu);
    }

    // Toggle subnav visibility
    for (const subnavBack of document.querySelectorAll('[data-subnav-back]')) {
        subnavBack.addEventListener('click', () => {
            subnavBack.parentNode.classList.remove('is-visible');
        });
    }

    for (const videomodal of document.querySelectorAll(VideoModal.selector())) {
        new VideoModal(videomodal);
    }

    for (const projectfilters of document.querySelectorAll(
        ProjectFilters.selector(),
    )) {
        new ProjectFilters(projectfilters);
    }

    for (const sticky of document.querySelectorAll(Sticky.selector())) {
        new Sticky(sticky);
    }

    for (const anchornav of document.querySelectorAll(AnchorNav.selector())) {
        new AnchorNav(anchornav);
    }

    for (const emailshare of document.querySelectorAll(EmailShare.selector())) {
        new EmailShare(emailshare);
    }

    for (const scholarshiplist of document.querySelectorAll(
        ScholarshipList.selector(),
    )) {
        new ScholarshipList(scholarshiplist);
    }

    for (const eventtoggleswitch of document.querySelectorAll(
        EventToggleSwitch.selector(),
    )) {
        new EventToggleSwitch(eventtoggleswitch);
    }

    for (const studymodetoggleswitch of document.querySelectorAll(
        ProgrammeToggleSwitch.selector(),
    )) {
        new ProgrammeToggleSwitch(studymodetoggleswitch);
    }

    for (const tablehint of document.querySelectorAll(TableHint.selector())) {
        new TableHint(tablehint);
    }

    for (const videoStream of document.querySelectorAll(VideoPlayer.selector())) {
        new VideoPlayer(videoStream);
    }

    new ActualHeight();
    Alpine.start();
});
