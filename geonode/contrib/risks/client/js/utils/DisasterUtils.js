/**
 * Copyright 2017, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
const React = require('react');
const {isString} = require('lodash');
const assign = require('object-assign');
function configLayer(baseurl, layerName, layerId, layerTitle, visibility = true, group) {
    return assign({
    "id": layerId,
    "type": "wms",
    "url": baseurl + "wms",
    "name": layerName,
    "title": layerTitle,
    "visibility": visibility,
    "format": "image/png",
    "tiled": true
    }, group && {group} || {});
}

function getViewParam({dim, showSubUnit, riskAnalysis} = {}) {
    const {dimensions} = riskAnalysis.riskAnalysisData.data;
    const {wms} = riskAnalysis;
    const dim1Val = dimensions[dim.dim1] && dimensions[dim.dim1].values[dim.dim1Idx];
    const dim2Val = dimensions[dim.dim2] && dimensions[dim.dim2].values[dim.dim2Idx];
    const dim1SearchDim = dimensions[dim.dim1] && dimensions[dim.dim1].layers[dim1Val] && dimensions[dim.dim1].layers[dim1Val].layerAttribute;
    const dim2SearchDim = dimensions[dim.dim2] && dimensions[dim.dim2].layers[dim2Val] && dimensions[dim.dim2].layers[dim2Val].layerAttribute;
    let viewparams = wms.viewparams.replace(`${dim1SearchDim}:{}`, `${dim1SearchDim}:${dim1Val}`).replace(`${dim2SearchDim}:{}`, `${dim2SearchDim}:${dim2Val}`);
    if (showSubUnit) {
        const admCode = viewparams.match(/(adm_code:)\w+/g)[0];
        const supCode = admCode.replace(/(adm_code:)/, "sub_adm_code:");
        const superCode = admCode.replace(/(adm_code:)/, "super_adm_code:");
        viewparams = viewparams.replace(admCode, `${supCode};${superCode}`);
    }
    return {viewparams};
}

function getLayerName({riskAnalysis}) {
    const {layer} = riskAnalysis.riskAnalysisData;
    return layer && layer.layerName;
}
function getStyle({riskAnalysis}) {
    const {layer} = riskAnalysis.riskAnalysisData;

    return layer.layerStyle && layer.layerStyle.name
}

function makeNotificationRow(data) {
    const attributes = Object.keys(data);
    attributes.sort();
    // ['abstract', 'category', 'date', 'details', 'license', 'text', 'thumbnail', 'title', 'uuid'];
    const match = ['abstract', 'category', 'details'];
    const links = ['details'];
    return attributes.filter((val) => {
        return match.indexOf(val) !== -1;
    }).map((item, idx) => {
        let obj = data[item];
        return isString(obj) ? (
            <div key={idx}>
            { links.indexOf(item) === -1 ? (
              <div>
                <div className="disaster-more-info-even">{item}</div>
                <div className="disaster-more-info-odd">{obj}</div>
              </div>
            ) : <a className="text-center" target="_blank" href={obj}>{item}</a>}
            </div>
        ) : null;
    });
}

function makeNotificationBlock(data) {
    return data.map((obj, idx) => {
        return (<div key={idx}><h4 className="disaster-more-info-table-title text-center">{obj.title}</h4>
            <div className="disaster-more-info-table">
                {makeNotificationRow(obj)}
            </div>
        </div>);
    });
}

function makeNotificationBody(data, title, head) {
    return (
        <div className="disaster-more-info-table-notification">
            {title}
            <div className="disaster-more-info-table-container">
                {head}
                {makeNotificationBlock(data)}
            </div>
        </div>
    );
}

module.exports = {configLayer, getViewParam, getLayerName, getStyle, makeNotificationBody};
