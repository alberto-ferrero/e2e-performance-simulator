#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os
from datetime import datetime

from ...utils.filemanager import getLogoPath, makeOutputFolder

#Import docx
from docx import Document
from docx.shared import Inches, Pt, Mm

""" E2E Performance Simulator post processor report writed """

def writeReport(simulationRequest: dict,
                outputReportFolderPath: str,
                outputDataFolderPath: str,
                outputPlotFolderPath: str):
    #Write report based on config request properties
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    section = doc.sections[0]
    section.left_margin = Mm(15)
    section.right_margin = Mm(15)

    #Add logo
    p = doc.add_paragraph()
    r = p.add_run()
    r.add_picture(os.path.join(getLogoPath(), "Logo.png"), width=Inches(3), )

    #First header page
    for i in range(3):
        doc.add_paragraph()
    title = 'E2E Performance Simulator Report'
    currentTime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    p = doc.add_paragraph()
    r = p.add_run(title)
    r.bold = True
    r.font.size = Pt(28)
    for i in range(12):
        doc.add_paragraph()
    
    p = doc.add_paragraph()
    r = p.add_run("RSN-SYS")
    r.bold = True
    r.font.size = Pt(20)
    
    p = doc.add_paragraph()
    r = p.add_run(currentTime)
    r.font.size = Pt(11)
    
    doc.add_page_break()

    #Add Section for the E2E Perfomances
    #TODO
    
    #Add Sections for each module
    modules: dict = simulationRequest['modules']
    for moduleTag, module in modules.items():

        if moduleTag == 'flightDynamics' and 'report' in module:
            #Add Flight Dynamics Results
            p = doc.add_paragraph()
            r = p.add_run("Flight Dynamics")
            r.bold = True
            r.font.size = Pt(16)

            p = doc.add_paragraph()
            r = p.add_run("Just writing satellites orbits, raw and unreadable from config :()")
            
            # Get for each satellite orbit plot
            for satellite in simulationRequest.get('satellites', []):
                
                #Get plot from plot folder
                #TODO
                p = doc.add_paragraph()
                r = p.add_run(satellite['id'] + "\n")
                r = p.add_run(satellite['orbit'])

            doc.add_page_break()

        if moduleTag == 'linkBudget' and 'report' in module:
            #Add Link Budget Results
            #TODO
            pass

        if moduleTag == 'regulatorMap' and 'report' in module:
            #Add Regulatory Mapper Results
            #TODO
            pass

        if moduleTag == 'networkTopology' and 'report' in module:
            #Add Network Topology Results
            #TODO
            pass

        if moduleTag == 'networkTopology' and 'report' in module:
            #Add Network Topology Results
            #TODO
            pass

        if moduleTag == 'airInterface' and 'report' in module:
            #Add Air Interface Results
            #TODO
            pass

    #Save doc
    makeOutputFolder(outputReportFolderPath)
    doc.save(os.path.join(outputReportFolderPath, "E2E_Performance_Simulator_Report.docx"))
    
# -*- coding: utf-8 -*-