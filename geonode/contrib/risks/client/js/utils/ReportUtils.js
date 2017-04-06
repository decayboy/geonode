/**
 * Copyright 2017, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

const {Promise} = require('es6-promise');
const canvg = require('canvg-browser');
const html2canvas = require('html2canvas');
function chartToImg(svg) {
    return new Promise(function(resolve, reject) {
        let svgOffsetX;
        let svgOffsetY;
        let svgH;
        let svgW;
        const svgCanv = document.createElement('canvas');
        const svgString = svg.outerHTML;
        [svgOffsetX = 0, svgOffsetY = 0, svgW =0, svgH = 0] = svg.getAttribute('viewBox').split(' ');
        svg.setAttribute("style", "");
        svgOffsetX = svgOffsetX ? svgOffsetX : 0;
        svgOffsetY = svgOffsetY ? svgOffsetY : 0;
        svgCanv.setAttribute("width", svgW);
        svgCanv.setAttribute("height", svgH);
        // svgCanv.getContext('2d').scale(2, 2);
        canvg(svgCanv, svgString, {
            ignoreMouse: true,
            ignoreAnimation: true,
            ignoreDimensions: true,
            ignoreClear: true,
            offsetX: svgOffsetX,
            offsetY: svgOffsetY,
            renderCallback: () => {
                try {
                    const data = svgCanv.toDataURL("image/png");
                    resolve({name: 'chart', data});
                }catch (e) {
                    reject(e);
                }
            }
            }
        );
    });
}
function legendToImg(img) {
    return new Promise(function(resolve, reject) {
        html2canvas(img, {
            logging: false,
            allowTaint: false,
            useCORS: true,
            onrendered: function(canvas) {
                try {
                    const data = canvas.toDataURL("img/png");
                    resolve({name: 'legend', data});
                }catch (e) {
                    reject(e);
                }
            }
        });
    });
}
module.exports = {chartToImg, legendToImg};
