!function(){function e(e,r,t){return(r=function(e){var r=function(e,r){if("object"!==a(e)||null===e)return e;var t=e[Symbol.toPrimitive];if(void 0!==t){var o=t.call(e,r||"default");if("object"!==a(o))return o;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===r?String:Number)(e)}(e,"string");return"symbol"===a(r)?r:String(r)}(r))in e?Object.defineProperty(e,r,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[r]=t,e}function r(e){return function(e){if(Array.isArray(e))return n(e)}(e)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(e)||o(e)||function(){throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}function t(e,r){return function(e){if(Array.isArray(e))return e}(e)||function(e,r){var t=null==e?null:"undefined"!=typeof Symbol&&e[Symbol.iterator]||e["@@iterator"];if(null!=t){var o,n,a,i,l=[],c=!0,s=!1;try{if(a=(t=t.call(e)).next,0===r){if(Object(t)!==t)return;c=!1}else for(;!(c=(o=a.call(t)).done)&&(l.push(o.value),l.length!==r);c=!0);}catch(d){s=!0,n=d}finally{try{if(!c&&null!=t.return&&(i=t.return(),Object(i)!==i))return}finally{if(s)throw n}}return l}}(e,r)||o(e,r)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}function o(e,r){if(e){if("string"==typeof e)return n(e,r);var t=Object.prototype.toString.call(e).slice(8,-1);return"Object"===t&&e.constructor&&(t=e.constructor.name),"Map"===t||"Set"===t?Array.from(e):"Arguments"===t||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t)?n(e,r):void 0}}function n(e,r){(null==r||r>e.length)&&(r=e.length);for(var t=0,o=new Array(r);t<r;t++)o[t]=e[t];return o}function a(e){return a="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},a(e)}System.register(["./index-legacy-2d3fc744.js","./useThemeProps-legacy-a789ba38.js","./Paper-legacy-121b08d0.js"],(function(o,n){"use strict";var i,l,c,s,d,u,m,h,g,f,p,y,v,S,b,C,k,w,A,T,x,B,P,I,E,F;return{setters:[function(e){i=e.z,l=e.A,c=e.B,s=e.D,d=e.E},function(e){u=e.u,m=e.T,h=e.a,g=e.f,f=e.d,p=e.c,y=e.b,v=e.e,S=e.g,b=e.l,C=e.h,k=e.i,w=e.j,A=e.k,o({alpha:e.i,createMuiTheme:e.t,createTheme:e.e,darken:e.g,decomposeColor:e.o,duration:e.v,easing:e.w,emphasize:e.h,getContrastRatio:e.q,getLuminance:e.s,hexToRgb:e.m,hslToRgb:e.n,lighten:e.l,recomposeColor:e.p,rgbToHex:e.r,useThemeProps:e.x})},function(e){T=e.C,x=e.c,B=e.G,P=e.d,I=e.T,E=e.u,F=e.g,o({css:e.a,experimentalStyled:e.s,keyframes:e.k,styled:e.s,useTheme:e.b})}],execute:function(){o({StyledEngineProvider:function(e){var r=e.injectFirst,t=e.children;return r?i(T,{value:n,children:t}):t},ThemeProvider:D,adaptV4Theme:function(r){var t=r.defaultProps,o=void 0===t?{}:t,n=r.mixins,a=void 0===n?{}:n,i=r.overrides,l=void 0===i?{}:i,d=r.palette,u=void 0===d?{}:d,m=r.props,h=void 0===m?{}:m,g=r.styleOverrides,f=void 0===g?{}:g,v=s(r,$),S=c({},v,{components:{}});Object.keys(o).forEach((function(e){var r=S.components[e]||{};r.defaultProps=o[e],S.components[e]=r})),Object.keys(h).forEach((function(e){var r=S.components[e]||{};r.defaultProps=h[e],S.components[e]=r})),Object.keys(f).forEach((function(e){var r=S.components[e]||{};r.styleOverrides=f[e],S.components[e]=r})),Object.keys(l).forEach((function(e){var r=S.components[e]||{};r.styleOverrides=l[e],S.components[e]=r})),S.spacing=p(r.spacing);var b=y(r.breakpoints||{}),C=S.spacing;S.mixins=c({gutters:function(){var r=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{};return c({paddingLeft:C(2),paddingRight:C(2)},r,e({},b.up("sm"),c({paddingLeft:C(3),paddingRight:C(3)},r[b.up("sm")])))}},a);var k=u.type,w=u.mode,A=s(u,J),T=w||k||"light";return S.palette=c({text:{hint:"dark"===T?"rgba(255, 255, 255, 0.5)":"rgba(0, 0, 0, 0.38)"},mode:T,type:T},A),S},createStyles:function(e){Q||(console.warn(["MUI: createStyles from @mui/material/styles is deprecated.","Please use @mui/styles/createStyles"].join("\n")),Q=!0);return e},experimental_extendTheme:de,experimental_sx:function(e){return function(r){var t=r.theme;return P({sx:e,theme:t})}},makeStyles:function(){throw new Error(g(14))},responsiveFontSizes:function(e){var r=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},t=r.breakpoints,o=void 0===t?["sm","md","lg"]:t,n=r.disableAlign,a=void 0!==n&&n,i=r.factor,l=void 0===i?2:i,s=r.variants,d=void 0===s?["h1","h2","h3","h4","h5","h6","subtitle1","subtitle2","body1","body2","caption","button","overline"]:s,u=c({},e);u.typography=c({},u.typography);var m=u.typography,h=ee(m.htmlFontSize),f=o.map((function(e){return u.breakpoints.values[e]}));return d.forEach((function(e){var r=m[e],t=parseFloat(h(r.fontSize,"rem"));if(!(t<=1)){var o=t,n=1+(o-1)/l,i=r.lineHeight;if(!X(i)&&!a)throw new Error(g(6));X(i)||(i=parseFloat(h(i,"rem"))/parseFloat(t));var s=null;a||(s=function(e){return re({size:e,grid:te({pixels:4,lineHeight:i,htmlFontSize:m.htmlFontSize})})}),m[e]=c({},r,oe({cssProperty:"fontSize",min:n,max:o,unit:"rem",breakpoints:f,transform:s}))}})),u},unstable_createMuiStrictModeTheme:function(e){for(var r=arguments.length,t=new Array(r>1?r-1:0),o=1;o<r;o++)t[o-1]=arguments[o];return v.apply(void 0,[f({unstable_strictMode:!0},e)].concat(t))},unstable_getUnit:Y,unstable_toUnitless:Z,withStyles:function(){throw new Error(g(15))},withTheme:function(){throw new Error(g(16))}});var n=x({key:"css",prepend:!0});function j(e){var r=e.styles,t=e.defaultTheme,o=void 0===t?{}:t;return i(B,{styles:"function"==typeof r?function(e){return r(null==(t=e)||0===Object.keys(t).length?o:e);var t}:r})}var M="function"==typeof Symbol&&Symbol.for?Symbol.for("mui.nested"):"__THEME_NESTED__";function L(e){var r=e.children,t=e.theme,o=u(),n=l.useMemo((function(){var e=null===o?t:function(e,r){return"function"==typeof r?r(e):c({},e,r)}(o,t);return null!=e&&(e[M]=null!==o),e}),[t,o]);return i(m.Provider,{value:n,children:r})}function O(e){var r=h();return i(I.Provider,{value:"object"===a(r)?r:{},children:e.children})}function D(e){var r=e.children,t=e.theme;return i(L,{theme:t,children:i(O,{children:r})})}var V=function(e,r,t){var o=arguments.length>3&&void 0!==arguments[3]?arguments[3]:[],n=e;r.forEach((function(e,i){i===r.length-1?Array.isArray(n)?n[Number(e)]=t:n&&"object"===a(n)&&(n[e]=t):n&&"object"===a(n)&&(n[e]||(n[e]=o.includes(e)?[]:{}),n=n[e])}))};function K(o,n){var i,l,c=n||{},s=c.prefix,d=c.shouldSkipGeneratingVar,u={},m={},h={};return i=function(r,t,o){if(("string"==typeof t||"number"==typeof t)&&(!d||d&&!d(r,t))){var n="--".concat(s?"".concat(s,"-"):"").concat(r.join("-"));Object.assign(u,e({},n,function(e,r){return"number"==typeof r?["lineHeight","fontWeight","opacity","zIndex"].some((function(r){return e.includes(r)}))||e[e.length-1].toLowerCase().indexOf("opacity")>=0?r:"".concat(r,"px"):r}(r,t))),V(m,r,"var(".concat(n,")"),o)}V(h,r,t,o)},l=function(e){return"vars"===e[0]},function e(o){var n=arguments.length>1&&void 0!==arguments[1]?arguments[1]:[],c=arguments.length>2&&void 0!==arguments[2]?arguments[2]:[];Object.entries(o).forEach((function(o){var s=t(o,2),d=s[0],u=s[1];(!l||l&&!l([].concat(r(n),[d])))&&null!=u&&("object"===a(u)&&Object.keys(u).length>0?e(u,[].concat(r(n),[d]),Array.isArray(u)?[].concat(r(c),[d]):c):i([].concat(r(n),[d]),u,c))}))}(o),{css:u,vars:m,parsedTheme:h}}var _="mode",z="color-scheme",H="data-color-scheme";function G(e){if("undefined"!=typeof window&&"system"===e)return window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"}function N(e,r){return"light"===e.mode||"system"===e.mode&&"light"===e.systemMode?r("light"):"dark"===e.mode||"system"===e.mode&&"dark"===e.systemMode?r("dark"):void 0}function R(e,r){if("undefined"!=typeof window){var t;try{t=localStorage.getItem(e)||void 0}catch(o){}return t||r}}function U(e){var r=e.defaultMode,o=void 0===r?"light":r,n=e.defaultLightColorScheme,a=e.defaultDarkColorScheme,i=e.supportedColorSchemes,s=void 0===i?[]:i,d=e.modeStorageKey,u=void 0===d?_:d,m=e.colorSchemeStorageKey,h=void 0===m?z:m,g=e.storageWindow,f=void 0===g?"undefined"==typeof window?void 0:window:g,p=s.join(","),y=t(l.useState((function(){var e=R(u,o);return{mode:e,systemMode:G(e),lightColorScheme:R("".concat(h,"-light"))||n,darkColorScheme:R("".concat(h,"-dark"))||a}})),2),v=y[0],S=y[1],b=function(e){return N(e,(function(r){return"light"===r?e.lightColorScheme:"dark"===r?e.darkColorScheme:void 0}))}(v),C=l.useCallback((function(e){S((function(r){var t=e||o;return e===r.mode?r:("undefined"!=typeof localStorage&&localStorage.setItem(u,t),c({},r,{mode:t,systemMode:G(t)}))}))}),[u,o]),k=l.useCallback((function(e){e&&"string"!=typeof e?e.light&&!p.includes(e.light)||e.dark&&!p.includes(e.dark)?console.error("`".concat(e,"` does not exist in `theme.colorSchemes`.")):(S((function(r){var t=c({},r);return(e.light||null===e.light)&&(t.lightColorScheme=null===e.light?n:e.light),(e.dark||null===e.dark)&&(t.darkColorScheme=null===e.dark?a:e.dark),t})),e.light&&localStorage.setItem("".concat(h,"-light"),e.light),e.dark&&localStorage.setItem("".concat(h,"-dark"),e.dark)):e&&!p.includes(e)?console.error("`".concat(e,"` does not exist in `theme.colorSchemes`.")):S((function(r){var t=c({},r);return e?(N(r,(function(r){localStorage.setItem("".concat(h,"-").concat(r),e),"light"===r&&(t.lightColorScheme=e),"dark"===r&&(t.darkColorScheme=e)})),t):(t.lightColorScheme=n,t.darkColorScheme=a,t)}))}),[p,h,n,a]),w=l.useCallback((function(e){"system"===v.mode&&S((function(r){return c({},r,{systemMode:null!=e&&e.matches?"dark":"light"})}))}),[v.mode]),A=l.useRef(w);return A.current=w,l.useEffect((function(){var e=function(){return A.current.apply(A,arguments)},r=window.matchMedia("(prefers-color-scheme: dark)");return r.addListener(e),e(r),function(){return r.removeListener(e)}}),[]),l.useEffect((function(){v.mode&&localStorage.setItem(u,v.mode),N(v,(function(e){"light"===e&&localStorage.setItem("".concat(h,"-light"),v.lightColorScheme),"dark"===e&&localStorage.setItem("".concat(h,"-dark"),v.darkColorScheme)}))}),[v,h,u]),l.useEffect((function(){var e=function(e){var r=e.newValue;"string"!=typeof e.key||!e.key.startsWith(h)||r&&!p.match(r)||(e.key.endsWith("light")&&k({light:r}),e.key.endsWith("dark")&&k({dark:r})),e.key!==u||r&&!["light","dark","system"].includes(r)||C(r||o)};if(f)return f.addEventListener("storage",e),function(){return f.removeEventListener("storage",e)}}),[k,C,u,h,p,o,f]),c({},v,{colorScheme:b,setMode:C,setColorScheme:k})}var W=["colorSchemes","components","cssVarPrefix"];function q(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"";function t(){for(var o=arguments.length,n=new Array(o),a=0;a<o;a++)n[a]=arguments[a];if(!n.length)return"";var i=n[0];return"string"!=typeof i||i.match(/(#|\(|\)|(-?(\d*\.)?\d+)(px|em|%|ex|ch|rem|vw|vh|vmin|vmax|cm|mm|in|pt|pc))/)?", ".concat(i):", var(--".concat(e?"".concat(e,"-"):"").concat(i).concat(t.apply(void 0,r(n.slice(1))),")")}var o=function(r){for(var o=arguments.length,n=new Array(o>1?o-1:0),a=1;a<o;a++)n[a-1]=arguments[a];return"var(--".concat(e?"".concat(e,"-"):"").concat(r).concat(t.apply(void 0,n),")")};return o}var $=["defaultProps","mixins","overrides","palette","props","styleOverrides"],J=["type","mode"];var Q=!1;function X(e){return String(parseFloat(e)).length===String(e).length}function Y(e){return String(e).match(/[\d.\-+]*\s*(.*)/)[1]||""}function Z(e){return parseFloat(e)}function ee(e){return function(r,t){var o=Y(r);if(o===t)return r;var n=Z(r);"px"!==o&&("em"===o||"rem"===o)&&(n=Z(r)*Z(e));var a=n;if("px"!==t)if("em"===t)a=n/Z(e);else{if("rem"!==t)return r;a=n/Z(e)}return parseFloat(a.toFixed(5))+t}}function re(e){var r=e.size,t=e.grid,o=r-r%t,n=o+t;return r-o<n-r?o:n}function te(e){var r=e.lineHeight;return e.pixels/(r*e.htmlFontSize)}function oe(r){var t=r.cssProperty,o=r.min,n=r.max,a=r.unit,i=void 0===a?"rem":a,l=r.breakpoints,c=void 0===l?[600,900,1200]:l,s=r.transform,d=void 0===s?null:s,u=e({},t,"".concat(o).concat(i)),m=(n-o)/c[c.length-1];return c.forEach((function(r){var n=o+m*r;null!==d&&(n=d(n)),u["@media (min-width:".concat(r,"px)")]=e({},t,"".concat(Math.round(1e4*n)/1e4).concat(i))})),u}var ne=["colorSchemes","cssVarPrefix"],ae=["palette"],ie=r(Array(25)).map((function(e,r){if(0!==r){var t=F(r);return"linear-gradient(rgba(255 255 255 / ".concat(t,"), rgba(255 255 255 / ").concat(t,"))")}}));function le(e,r){r.forEach((function(r){e[r]||(e[r]={})}))}function ce(e,r,t){e[r]=e[r]||t}var se=function(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"mui";return q(e)};function de(){var e,r,t,o,n,a,i=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},l=i.colorSchemes,d=void 0===l?{}:l,u=i.cssVarPrefix,m=void 0===u?"mui":u,h=s(i,ne),g=se(m),p=v(c({},h,d.light&&{palette:null==(e=d.light)?void 0:e.palette})),y=p.palette,A=s(p,ae),T=v({palette:c({mode:"dark"},null==(r=d.dark)?void 0:r.palette)}),x=T.palette,B=c({},A,{cssVarPrefix:m,getCssVar:g,colorSchemes:c({},d,{light:c({},d.light,{palette:y,opacity:c({inputPlaceholder:.42,inputUnderline:.42,switchTrackDisabled:.12,switchTrack:.38},null==(t=d.light)?void 0:t.opacity),overlays:(null==(o=d.light)?void 0:o.overlays)||[]}),dark:c({},d.dark,{palette:x,opacity:c({inputPlaceholder:.5,inputUnderline:.7,switchTrackDisabled:.2,switchTrack:.3},null==(n=d.dark)?void 0:n.opacity),overlays:(null==(a=d.dark)?void 0:a.overlays)||ie})})});Object.keys(B.colorSchemes).forEach((function(e){var r=B.colorSchemes[e].palette;if("light"===e?(ce(r.common,"background","#fff"),ce(r.common,"onBackground","#000")):(ce(r.common,"background","#000"),ce(r.common,"onBackground","#fff")),le(r,["Alert","AppBar","Avatar","Chip","FilledInput","LinearProgress","Skeleton","Slider","SnackbarContent","SpeedDialAction","StepConnector","StepContent","Switch","TableCell","Tooltip"]),"light"===e){ce(r.Alert,"errorColor",S(r.error.light,.6)),ce(r.Alert,"infoColor",S(r.info.light,.6)),ce(r.Alert,"successColor",S(r.success.light,.6)),ce(r.Alert,"warningColor",S(r.warning.light,.6)),ce(r.Alert,"errorFilledBg",g("palette-error-main")),ce(r.Alert,"infoFilledBg",g("palette-info-main")),ce(r.Alert,"successFilledBg",g("palette-success-main")),ce(r.Alert,"warningFilledBg",g("palette-warning-main")),ce(r.Alert,"errorFilledColor",y.getContrastText(r.error.main)),ce(r.Alert,"infoFilledColor",y.getContrastText(r.info.main)),ce(r.Alert,"successFilledColor",y.getContrastText(r.success.main)),ce(r.Alert,"warningFilledColor",y.getContrastText(r.warning.main)),ce(r.Alert,"errorStandardBg",b(r.error.light,.9)),ce(r.Alert,"infoStandardBg",b(r.info.light,.9)),ce(r.Alert,"successStandardBg",b(r.success.light,.9)),ce(r.Alert,"warningStandardBg",b(r.warning.light,.9)),ce(r.Alert,"errorIconColor",g("palette-error-light")),ce(r.Alert,"infoIconColor",g("palette-info-light")),ce(r.Alert,"successIconColor",g("palette-success-light")),ce(r.Alert,"warningIconColor",g("palette-warning-light")),ce(r.AppBar,"defaultBg",g("palette-grey-100")),ce(r.Avatar,"defaultBg",g("palette-grey-400")),ce(r.Chip,"defaultBorder",g("palette-grey-400")),ce(r.Chip,"defaultAvatarColor",g("palette-grey-700")),ce(r.Chip,"defaultIconColor",g("palette-grey-700")),ce(r.FilledInput,"bg","rgba(0, 0, 0, 0.06)"),ce(r.FilledInput,"hoverBg","rgba(0, 0, 0, 0.09)"),ce(r.FilledInput,"disabledBg","rgba(0, 0, 0, 0.12)"),ce(r.LinearProgress,"primaryBg",b(r.primary.main,.62)),ce(r.LinearProgress,"secondaryBg",b(r.secondary.main,.62)),ce(r.LinearProgress,"errorBg",b(r.error.main,.62)),ce(r.LinearProgress,"infoBg",b(r.info.main,.62)),ce(r.LinearProgress,"successBg",b(r.success.main,.62)),ce(r.LinearProgress,"warningBg",b(r.warning.main,.62)),ce(r.Skeleton,"bg","rgba(".concat(g("palette-text-primaryChannel")," / 0.11)")),ce(r.Slider,"primaryTrack",b(r.primary.main,.62)),ce(r.Slider,"secondaryTrack",b(r.secondary.main,.62)),ce(r.Slider,"errorTrack",b(r.error.main,.62)),ce(r.Slider,"infoTrack",b(r.info.main,.62)),ce(r.Slider,"successTrack",b(r.success.main,.62)),ce(r.Slider,"warningTrack",b(r.warning.main,.62));var t=C(r.background.default,.8);ce(r.SnackbarContent,"bg",t),ce(r.SnackbarContent,"color",y.getContrastText(t)),ce(r.SpeedDialAction,"fabHoverBg",C(r.background.paper,.15)),ce(r.StepConnector,"border",g("palette-grey-400")),ce(r.StepContent,"border",g("palette-grey-400")),ce(r.Switch,"defaultColor",g("palette-common-white")),ce(r.Switch,"defaultDisabledColor",g("palette-grey-100")),ce(r.Switch,"primaryDisabledColor",b(r.primary.main,.62)),ce(r.Switch,"secondaryDisabledColor",b(r.secondary.main,.62)),ce(r.Switch,"errorDisabledColor",b(r.error.main,.62)),ce(r.Switch,"infoDisabledColor",b(r.info.main,.62)),ce(r.Switch,"successDisabledColor",b(r.success.main,.62)),ce(r.Switch,"warningDisabledColor",b(r.warning.main,.62)),ce(r.TableCell,"border",b(k(r.divider,1),.88)),ce(r.Tooltip,"bg",k(r.grey[700],.92))}else{ce(r.Alert,"errorColor",b(r.error.light,.6)),ce(r.Alert,"infoColor",b(r.info.light,.6)),ce(r.Alert,"successColor",b(r.success.light,.6)),ce(r.Alert,"warningColor",b(r.warning.light,.6)),ce(r.Alert,"errorFilledBg",g("palette-error-dark")),ce(r.Alert,"infoFilledBg",g("palette-info-dark")),ce(r.Alert,"successFilledBg",g("palette-success-dark")),ce(r.Alert,"warningFilledBg",g("palette-warning-dark")),ce(r.Alert,"errorFilledColor",x.getContrastText(r.error.dark)),ce(r.Alert,"infoFilledColor",x.getContrastText(r.info.dark)),ce(r.Alert,"successFilledColor",x.getContrastText(r.success.dark)),ce(r.Alert,"warningFilledColor",x.getContrastText(r.warning.dark)),ce(r.Alert,"errorStandardBg",S(r.error.light,.9)),ce(r.Alert,"infoStandardBg",S(r.info.light,.9)),ce(r.Alert,"successStandardBg",S(r.success.light,.9)),ce(r.Alert,"warningStandardBg",S(r.warning.light,.9)),ce(r.Alert,"errorIconColor",g("palette-error-main")),ce(r.Alert,"infoIconColor",g("palette-info-main")),ce(r.Alert,"successIconColor",g("palette-success-main")),ce(r.Alert,"warningIconColor",g("palette-warning-main")),ce(r.AppBar,"defaultBg",g("palette-grey-900")),ce(r.AppBar,"darkBg",g("palette-background-paper")),ce(r.AppBar,"darkColor",g("palette-text-primary")),ce(r.Avatar,"defaultBg",g("palette-grey-600")),ce(r.Chip,"defaultBorder",g("palette-grey-700")),ce(r.Chip,"defaultAvatarColor",g("palette-grey-300")),ce(r.Chip,"defaultIconColor",g("palette-grey-300")),ce(r.FilledInput,"bg","rgba(255, 255, 255, 0.09)"),ce(r.FilledInput,"hoverBg","rgba(255, 255, 255, 0.13)"),ce(r.FilledInput,"disabledBg","rgba(255, 255, 255, 0.12)"),ce(r.LinearProgress,"primaryBg",S(r.primary.main,.5)),ce(r.LinearProgress,"secondaryBg",S(r.secondary.main,.5)),ce(r.LinearProgress,"errorBg",S(r.error.main,.5)),ce(r.LinearProgress,"infoBg",S(r.info.main,.5)),ce(r.LinearProgress,"successBg",S(r.success.main,.5)),ce(r.LinearProgress,"warningBg",S(r.warning.main,.5)),ce(r.Skeleton,"bg","rgba(".concat(g("palette-text-primaryChannel")," / 0.13)")),ce(r.Slider,"primaryTrack",S(r.primary.main,.5)),ce(r.Slider,"secondaryTrack",S(r.secondary.main,.5)),ce(r.Slider,"errorTrack",S(r.error.main,.5)),ce(r.Slider,"infoTrack",S(r.info.main,.5)),ce(r.Slider,"successTrack",S(r.success.main,.5)),ce(r.Slider,"warningTrack",S(r.warning.main,.5));var o=C(r.background.default,.98);ce(r.SnackbarContent,"bg",o),ce(r.SnackbarContent,"color",x.getContrastText(o)),ce(r.SpeedDialAction,"fabHoverBg",C(r.background.paper,.15)),ce(r.StepConnector,"border",g("palette-grey-600")),ce(r.StepContent,"border",g("palette-grey-600")),ce(r.Switch,"defaultColor",g("palette-grey-300")),ce(r.Switch,"defaultDisabledColor",g("palette-grey-600")),ce(r.Switch,"primaryDisabledColor",S(r.primary.main,.55)),ce(r.Switch,"secondaryDisabledColor",S(r.secondary.main,.55)),ce(r.Switch,"errorDisabledColor",S(r.error.main,.55)),ce(r.Switch,"infoDisabledColor",S(r.info.main,.55)),ce(r.Switch,"successDisabledColor",S(r.success.main,.55)),ce(r.Switch,"warningDisabledColor",S(r.warning.main,.55)),ce(r.TableCell,"border",S(k(r.divider,1),.68)),ce(r.Tooltip,"bg",k(r.grey[700],.92))}r.common.backgroundChannel=w(r.common.background),r.common.onBackgroundChannel=w(r.common.onBackground),r.dividerChannel=w(r.divider),Object.keys(r).forEach((function(e){var t=r[e];t.main&&(r[e].mainChannel=w(t.main)),t.light&&(r[e].lightChannel=w(t.light)),t.dark&&(r[e].darkChannel=w(t.dark)),t.contrastText&&(r[e].contrastTextChannel=w(t.contrastText)),t.primary&&(r[e].primaryChannel=w(t.primary)),t.secondary&&(r[e].secondaryChannel=w(t.secondary)),t.active&&(r[e].activeChannel=w(t.active)),t.selected&&(r[e].selectedChannel=w(t.selected))}))}));for(var P=arguments.length,I=new Array(P>1?P-1:0),E=1;E<P;E++)I[E-1]=arguments[E];return B=I.reduce((function(e,r){return f(e,r)}),B)}var ue=o("shouldSkipGeneratingVar",(function(e){var r;return!!e[0].match(/(typography|mixins|breakpoints|direction|transitions)/)||"palette"===e[0]&&!(null==(r=e[1])||!r.match(/(mode|contrastThreshold|tonalOffset)/))})),me=function(r){var o=r.theme,n=void 0===o?{}:o,u=r.attribute,m=void 0===u?H:u,h=r.modeStorageKey,p=void 0===h?_:h,y=r.colorSchemeStorageKey,v=void 0===y?z:y,S=r.defaultMode,b=void 0===S?"light":S,C=r.defaultColorScheme,k=r.disableTransitionOnChange,w=void 0!==k&&k,A=r.enableColorScheme,T=void 0===A||A,x=r.shouldSkipGeneratingVar,B=r.resolveTheme;(!n.colorSchemes||"string"==typeof C&&!n.colorSchemes[C]||"object"===a(C)&&!n.colorSchemes[null==C?void 0:C.light]||"object"===a(C)&&!n.colorSchemes[null==C?void 0:C.dark])&&console.error("MUI: `".concat(C,"` does not exist in `theme.colorSchemes`."));var P=l.createContext(void 0);return{CssVarsProvider:function(r){var o=r.children,a=r.theme,u=void 0===a?n:a,h=r.modeStorageKey,g=void 0===h?p:h,y=r.colorSchemeStorageKey,S=void 0===y?v:y,k=r.attribute,A=void 0===k?m:k,I=r.defaultMode,F=void 0===I?b:I,M=r.defaultColorScheme,L=void 0===M?C:M,O=r.disableTransitionOnChange,V=void 0===O?w:O,_=r.enableColorScheme,z=void 0===_?T:_,H=r.storageWindow,G=void 0===H?"undefined"==typeof window?void 0:window:H,N=r.documentNode,R=void 0===N?"undefined"==typeof document?void 0:document:N,q=r.colorSchemeNode,$=void 0===q?"undefined"==typeof document?void 0:document.documentElement:q,J=r.colorSchemeSelector,Q=void 0===J?":root":J,X=r.shouldSkipGeneratingVar,Y=void 0===X?x:X,Z=l.useRef(!1),ee=u.colorSchemes,re=void 0===ee?{}:ee,te=u.components,oe=void 0===te?{}:te,ne=u.cssVarPrefix,ae=s(u,W),ie=Object.keys(re),le="string"==typeof L?L:L.light,ce="string"==typeof L?L:L.dark,se=U({supportedColorSchemes:ie,defaultLightColorScheme:le,defaultDarkColorScheme:ce,modeStorageKey:g,colorSchemeStorageKey:S,defaultMode:F,storageWindow:G}),de=se.mode,ue=se.setMode,me=se.systemMode,he=se.lightColorScheme,ge=se.darkColorScheme,fe=se.colorScheme,pe=se.setColorScheme,ye=fe||("dark"===F?ce:le),ve=ae,Se=K(ve,{prefix:ne,shouldSkipGeneratingVar:Y}),be=Se.css,Ce=Se.vars,ke=Se.parsedTheme;ve=c({},ke,{components:oe,colorSchemes:re,cssVarPrefix:ne,vars:Ce,getColorSchemeSelector:function(e){return"[".concat(A,'="').concat(e,'"] &')}});var we={},Ae={};return Object.entries(re).forEach((function(e){var r=t(e,2),o=r[0],n=K(r[1],{prefix:ne,shouldSkipGeneratingVar:Y}),a=n.css,i=n.vars,l=n.parsedTheme;ve.vars=f(ve.vars,i),o===ye&&(ve=c({},ve,l)).palette&&(ve.palette.mode=de,ve.palette.colorScheme=ye),o===("string"==typeof L?L:"dark"===F?L.dark:L.light)?we["".concat(Q,", [").concat(A,'="').concat(o,'"]')]=a:Ae["".concat(":root"===Q?"":Q,"[").concat(A,'="').concat(o,'"]')]=a})),l.useEffect((function(){fe&&$&&$.setAttribute(A,fe)}),[fe,A,$]),E((function(){if(de&&z&&$){var e=$.style.getPropertyValue("color-scheme");return"system"===de?$.style.setProperty("color-scheme",me):$.style.setProperty("color-scheme",de),function(){$.style.setProperty("color-scheme",e)}}}),[de,me,z,$]),l.useEffect((function(){var e;if(V&&Z.current&&R){var r=R.createElement("style");r.appendChild(R.createTextNode("*{-webkit-transition:none!important;-moz-transition:none!important;-o-transition:none!important;-ms-transition:none!important;transition:none!important}")),R.head.appendChild(r),window.getComputedStyle(R.body),e=setTimeout((function(){R.head.removeChild(r)}),1)}return function(){clearTimeout(e)}}),[fe,V,R]),l.useEffect((function(){return Z.current=!0,function(){Z.current=!1}}),[]),d(P.Provider,{value:{mode:de,setMode:ue,lightColorScheme:he,darkColorScheme:ge,colorScheme:fe,setColorScheme:pe,allColorSchemes:ie},children:[i(j,{styles:e({},Q,be)}),i(j,{styles:we}),i(j,{styles:Ae}),i(D,{theme:B?B(ve):ve,children:o})]})},useColorScheme:function(){var e=l.useContext(P);if(!e)throw new Error(g(19));return e},getInitColorSchemeScript:function(e){return function(e){var r=e||{},t=r.enableColorScheme,o=void 0===t||t,n=r.enableSystem,a=void 0!==n&&n,l=r.defaultLightColorScheme,c=void 0===l?"light":l,s=r.defaultDarkColorScheme,d=void 0===s?"dark":s,u=r.modeStorageKey,m=void 0===u?_:u,h=r.colorSchemeStorageKey,g=void 0===h?z:h,f=r.attribute,p=void 0===f?H:f,y=r.colorSchemeNode,v=void 0===y?"document.documentElement":y;return i("script",{dangerouslySetInnerHTML:{__html:"(function() { try {\n        var mode = localStorage.getItem('".concat(m,"');\n        var cssColorScheme = mode;\n        var colorScheme = '';\n        if (mode === 'system' || (!mode && !!").concat(a,")) {\n          // handle system mode\n          var mql = window.matchMedia('(prefers-color-scheme: dark)');\n          if (mql.matches) {\n            cssColorScheme = 'dark';\n            colorScheme = localStorage.getItem('").concat(g,"-dark') || '").concat(d,"';\n          } else {\n            cssColorScheme = 'light';\n            colorScheme = localStorage.getItem('").concat(g,"-light') || '").concat(c,"';\n          }\n        }\n        if (mode === 'light') {\n          colorScheme = localStorage.getItem('").concat(g,"-light') || '").concat(c,"';\n        }\n        if (mode === 'dark') {\n          colorScheme = localStorage.getItem('").concat(g,"-dark') || '").concat(d,"';\n        }\n        if (colorScheme) {\n          ").concat(v,".setAttribute('").concat(p,"', colorScheme);\n        }\n        if (").concat(o," && !!cssColorScheme) {\n          ").concat(v,".style.setProperty('color-scheme', cssColorScheme);\n        }\n      } catch (e) {} })();")}})}(c({attribute:m,colorSchemeStorageKey:v,modeStorageKey:p,enableColorScheme:T},e))}}}({theme:de(),attribute:"data-mui-color-scheme",modeStorageKey:"mui-mode",colorSchemeStorageKey:"mui-color-scheme",defaultColorScheme:{light:"light",dark:"dark"},resolveTheme:function(e){return c({},e,{typography:A(e.palette,e.typography)})},shouldSkipGeneratingVar:ue}),he=me.CssVarsProvider,ge=me.useColorScheme,fe=me.getInitColorSchemeScript;o({Experimental_CssVarsProvider:he,useColorScheme:ge,getInitColorSchemeScript:fe})}}}))}();
