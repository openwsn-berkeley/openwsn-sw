#
# Generated Makefile - do not edit!
#
# Edit the Makefile in the project folder instead (../Makefile). Each target
# has a -pre and a -post target defined where you can add customized code.
#
# This makefile implements configuration specific macros and targets.


# Include project Makefile
include Makefile
# Include makefile containing local settings
ifeq "$(wildcard nbproject/Makefile-local-default.mk)" "nbproject/Makefile-local-default.mk"
include nbproject/Makefile-local-default.mk
endif

# Environment
MKDIR=mkdir -p
RM=rm -f 
MV=mv 
CP=cp 

# Macros
CND_CONF=default
ifeq ($(TYPE_IMAGE), DEBUG_RUN)
IMAGE_TYPE=debug
OUTPUT_SUFFIX=cof
DEBUGGABLE_SUFFIX=cof
FINAL_IMAGE=dist/${CND_CONF}/${IMAGE_TYPE}/current_monitor.X.${IMAGE_TYPE}.${OUTPUT_SUFFIX}
else
IMAGE_TYPE=production
OUTPUT_SUFFIX=hex
DEBUGGABLE_SUFFIX=cof
FINAL_IMAGE=dist/${CND_CONF}/${IMAGE_TYPE}/current_monitor.X.${IMAGE_TYPE}.${OUTPUT_SUFFIX}
endif

# Object Directory
OBJECTDIR=build/${CND_CONF}/${IMAGE_TYPE}

# Distribution Directory
DISTDIR=dist/${CND_CONF}/${IMAGE_TYPE}

# Object Files Quoted if spaced
OBJECTFILES_QUOTED_IF_SPACED=${OBJECTDIR}/src/Drivers/xbee.o ${OBJECTDIR}/src/Drivers/currentADC.o ${OBJECTDIR}/src/Drivers/rtc.o ${OBJECTDIR}/_ext/1888179439/usb_function_cdc.o "${OBJECTDIR}/src/Microchip/USB/Generic Device Driver/usb_function_generic.o" ${OBJECTDIR}/_ext/1534649548/usb_device.o ${OBJECTDIR}/src/Services/usb2serial.o ${OBJECTDIR}/src/Services/commands.o ${OBJECTDIR}/src/Services/commands_xbee.o ${OBJECTDIR}/src/Services/commands_adc.o ${OBJECTDIR}/_ext/876597078/main.o ${OBJECTDIR}/_ext/876597078/usb_descriptors.o ${OBJECTDIR}/src/usb_memory.o ${OBJECTDIR}/src/Drivers/atflash.o ${OBJECTDIR}/src/Drivers/SPI.o ${OBJECTDIR}/src/Services/commands_flash.o
POSSIBLE_DEPFILES=${OBJECTDIR}/src/Drivers/xbee.o.d ${OBJECTDIR}/src/Drivers/currentADC.o.d ${OBJECTDIR}/src/Drivers/rtc.o.d ${OBJECTDIR}/_ext/1888179439/usb_function_cdc.o.d "${OBJECTDIR}/src/Microchip/USB/Generic Device Driver/usb_function_generic.o.d" ${OBJECTDIR}/_ext/1534649548/usb_device.o.d ${OBJECTDIR}/src/Services/usb2serial.o.d ${OBJECTDIR}/src/Services/commands.o.d ${OBJECTDIR}/src/Services/commands_xbee.o.d ${OBJECTDIR}/src/Services/commands_adc.o.d ${OBJECTDIR}/_ext/876597078/main.o.d ${OBJECTDIR}/_ext/876597078/usb_descriptors.o.d ${OBJECTDIR}/src/usb_memory.o.d ${OBJECTDIR}/src/Drivers/atflash.o.d ${OBJECTDIR}/src/Drivers/SPI.o.d ${OBJECTDIR}/src/Services/commands_flash.o.d

# Object Files
OBJECTFILES=${OBJECTDIR}/src/Drivers/xbee.o ${OBJECTDIR}/src/Drivers/currentADC.o ${OBJECTDIR}/src/Drivers/rtc.o ${OBJECTDIR}/_ext/1888179439/usb_function_cdc.o ${OBJECTDIR}/src/Microchip/USB/Generic\ Device\ Driver/usb_function_generic.o ${OBJECTDIR}/_ext/1534649548/usb_device.o ${OBJECTDIR}/src/Services/usb2serial.o ${OBJECTDIR}/src/Services/commands.o ${OBJECTDIR}/src/Services/commands_xbee.o ${OBJECTDIR}/src/Services/commands_adc.o ${OBJECTDIR}/_ext/876597078/main.o ${OBJECTDIR}/_ext/876597078/usb_descriptors.o ${OBJECTDIR}/src/usb_memory.o ${OBJECTDIR}/src/Drivers/atflash.o ${OBJECTDIR}/src/Drivers/SPI.o ${OBJECTDIR}/src/Services/commands_flash.o


CFLAGS=
ASFLAGS=
LDLIBSOPTIONS=

############# Tool locations ##########################################
# If you copy a project from one host to another, the path where the  #
# compiler is installed may be different.                             #
# If you open this project with MPLAB X in the new host, this         #
# makefile will be regenerated and the paths will be corrected.       #
#######################################################################
# fixDeps replaces a bunch of sed/cat/printf statements that slow down the build
FIXDEPS=fixDeps

.build-conf:  ${BUILD_SUBPROJECTS}
	${MAKE}  -f nbproject/Makefile-default.mk dist/${CND_CONF}/${IMAGE_TYPE}/current_monitor.X.${IMAGE_TYPE}.${OUTPUT_SUFFIX}

MP_PROCESSOR_OPTION=18F26J50
MP_PROCESSOR_OPTION_LD=18f26j50
MP_LINKER_DEBUG_OPTION=
# ------------------------------------------------------------------------------------
# Rules for buildStep: assemble
ifeq ($(TYPE_IMAGE), DEBUG_RUN)
else
endif

# ------------------------------------------------------------------------------------
# Rules for buildStep: compile
ifeq ($(TYPE_IMAGE), DEBUG_RUN)
${OBJECTDIR}/src/Drivers/xbee.o: src/Drivers/xbee.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Drivers 
	@${RM} ${OBJECTDIR}/src/Drivers/xbee.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Drivers/xbee.o   src/Drivers/xbee.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Drivers/xbee.o 
	
${OBJECTDIR}/src/Drivers/currentADC.o: src/Drivers/currentADC.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Drivers 
	@${RM} ${OBJECTDIR}/src/Drivers/currentADC.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Drivers/currentADC.o   src/Drivers/currentADC.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Drivers/currentADC.o 
	
${OBJECTDIR}/src/Drivers/rtc.o: src/Drivers/rtc.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Drivers 
	@${RM} ${OBJECTDIR}/src/Drivers/rtc.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Drivers/rtc.o   src/Drivers/rtc.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Drivers/rtc.o 
	
${OBJECTDIR}/_ext/1888179439/usb_function_cdc.o: /mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/USB/CDC\ Device\ Driver/usb_function_cdc.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/1888179439 
	@${RM} ${OBJECTDIR}/_ext/1888179439/usb_function_cdc.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/_ext/1888179439/usb_function_cdc.o   "/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/USB/CDC Device Driver/usb_function_cdc.c" 
	@${DEP_GEN} -d ${OBJECTDIR}/_ext/1888179439/usb_function_cdc.o 
	
${OBJECTDIR}/src/Microchip/USB/Generic\ Device\ Driver/usb_function_generic.o: src/Microchip/USB/Generic\ Device\ Driver/usb_function_generic.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Microchip/USB/Generic\ Device\ Driver 
	@${RM} ${OBJECTDIR}/src/Microchip/USB/Generic\ Device\ Driver/usb_function_generic.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo "${OBJECTDIR}/src/Microchip/USB/Generic Device Driver/usb_function_generic.o"   "src/Microchip/USB/Generic Device Driver/usb_function_generic.c" 
	@${DEP_GEN} -d "${OBJECTDIR}/src/Microchip/USB/Generic Device Driver/usb_function_generic.o" 
	
${OBJECTDIR}/_ext/1534649548/usb_device.o: /mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/USB/usb_device.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/1534649548 
	@${RM} ${OBJECTDIR}/_ext/1534649548/usb_device.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/_ext/1534649548/usb_device.o   /mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/USB/usb_device.c 
	@${DEP_GEN} -d ${OBJECTDIR}/_ext/1534649548/usb_device.o 
	
${OBJECTDIR}/src/Services/usb2serial.o: src/Services/usb2serial.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Services 
	@${RM} ${OBJECTDIR}/src/Services/usb2serial.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Services/usb2serial.o   src/Services/usb2serial.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Services/usb2serial.o 
	
${OBJECTDIR}/src/Services/commands.o: src/Services/commands.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Services 
	@${RM} ${OBJECTDIR}/src/Services/commands.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Services/commands.o   src/Services/commands.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Services/commands.o 
	
${OBJECTDIR}/src/Services/commands_xbee.o: src/Services/commands_xbee.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Services 
	@${RM} ${OBJECTDIR}/src/Services/commands_xbee.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Services/commands_xbee.o   src/Services/commands_xbee.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Services/commands_xbee.o 
	
${OBJECTDIR}/src/Services/commands_adc.o: src/Services/commands_adc.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Services 
	@${RM} ${OBJECTDIR}/src/Services/commands_adc.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Services/commands_adc.o   src/Services/commands_adc.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Services/commands_adc.o 
	
${OBJECTDIR}/_ext/876597078/main.o: /mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/main.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/876597078 
	@${RM} ${OBJECTDIR}/_ext/876597078/main.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/_ext/876597078/main.o   /mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/main.c 
	@${DEP_GEN} -d ${OBJECTDIR}/_ext/876597078/main.o 
	
${OBJECTDIR}/_ext/876597078/usb_descriptors.o: /mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/usb_descriptors.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/876597078 
	@${RM} ${OBJECTDIR}/_ext/876597078/usb_descriptors.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/_ext/876597078/usb_descriptors.o   /mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/usb_descriptors.c 
	@${DEP_GEN} -d ${OBJECTDIR}/_ext/876597078/usb_descriptors.o 
	
${OBJECTDIR}/src/usb_memory.o: src/usb_memory.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src 
	@${RM} ${OBJECTDIR}/src/usb_memory.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/usb_memory.o   src/usb_memory.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/usb_memory.o 
	
${OBJECTDIR}/src/Drivers/atflash.o: src/Drivers/atflash.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Drivers 
	@${RM} ${OBJECTDIR}/src/Drivers/atflash.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Drivers/atflash.o   src/Drivers/atflash.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Drivers/atflash.o 
	
${OBJECTDIR}/src/Drivers/SPI.o: src/Drivers/SPI.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Drivers 
	@${RM} ${OBJECTDIR}/src/Drivers/SPI.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Drivers/SPI.o   src/Drivers/SPI.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Drivers/SPI.o 
	
${OBJECTDIR}/src/Services/commands_flash.o: src/Services/commands_flash.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Services 
	@${RM} ${OBJECTDIR}/src/Services/commands_flash.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -D__DEBUG -D__MPLAB_DEBUGGER_PK3=1 -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Services/commands_flash.o   src/Services/commands_flash.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Services/commands_flash.o 
	
else
${OBJECTDIR}/src/Drivers/xbee.o: src/Drivers/xbee.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Drivers 
	@${RM} ${OBJECTDIR}/src/Drivers/xbee.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Drivers/xbee.o   src/Drivers/xbee.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Drivers/xbee.o 
	
${OBJECTDIR}/src/Drivers/currentADC.o: src/Drivers/currentADC.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Drivers 
	@${RM} ${OBJECTDIR}/src/Drivers/currentADC.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Drivers/currentADC.o   src/Drivers/currentADC.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Drivers/currentADC.o 
	
${OBJECTDIR}/src/Drivers/rtc.o: src/Drivers/rtc.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Drivers 
	@${RM} ${OBJECTDIR}/src/Drivers/rtc.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Drivers/rtc.o   src/Drivers/rtc.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Drivers/rtc.o 
	
${OBJECTDIR}/_ext/1888179439/usb_function_cdc.o: /mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/USB/CDC\ Device\ Driver/usb_function_cdc.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/1888179439 
	@${RM} ${OBJECTDIR}/_ext/1888179439/usb_function_cdc.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/_ext/1888179439/usb_function_cdc.o   "/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/USB/CDC Device Driver/usb_function_cdc.c" 
	@${DEP_GEN} -d ${OBJECTDIR}/_ext/1888179439/usb_function_cdc.o 
	
${OBJECTDIR}/src/Microchip/USB/Generic\ Device\ Driver/usb_function_generic.o: src/Microchip/USB/Generic\ Device\ Driver/usb_function_generic.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Microchip/USB/Generic\ Device\ Driver 
	@${RM} ${OBJECTDIR}/src/Microchip/USB/Generic\ Device\ Driver/usb_function_generic.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo "${OBJECTDIR}/src/Microchip/USB/Generic Device Driver/usb_function_generic.o"   "src/Microchip/USB/Generic Device Driver/usb_function_generic.c" 
	@${DEP_GEN} -d "${OBJECTDIR}/src/Microchip/USB/Generic Device Driver/usb_function_generic.o" 
	
${OBJECTDIR}/_ext/1534649548/usb_device.o: /mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/USB/usb_device.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/1534649548 
	@${RM} ${OBJECTDIR}/_ext/1534649548/usb_device.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/_ext/1534649548/usb_device.o   /mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/USB/usb_device.c 
	@${DEP_GEN} -d ${OBJECTDIR}/_ext/1534649548/usb_device.o 
	
${OBJECTDIR}/src/Services/usb2serial.o: src/Services/usb2serial.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Services 
	@${RM} ${OBJECTDIR}/src/Services/usb2serial.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Services/usb2serial.o   src/Services/usb2serial.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Services/usb2serial.o 
	
${OBJECTDIR}/src/Services/commands.o: src/Services/commands.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Services 
	@${RM} ${OBJECTDIR}/src/Services/commands.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Services/commands.o   src/Services/commands.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Services/commands.o 
	
${OBJECTDIR}/src/Services/commands_xbee.o: src/Services/commands_xbee.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Services 
	@${RM} ${OBJECTDIR}/src/Services/commands_xbee.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Services/commands_xbee.o   src/Services/commands_xbee.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Services/commands_xbee.o 
	
${OBJECTDIR}/src/Services/commands_adc.o: src/Services/commands_adc.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Services 
	@${RM} ${OBJECTDIR}/src/Services/commands_adc.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Services/commands_adc.o   src/Services/commands_adc.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Services/commands_adc.o 
	
${OBJECTDIR}/_ext/876597078/main.o: /mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/main.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/876597078 
	@${RM} ${OBJECTDIR}/_ext/876597078/main.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/_ext/876597078/main.o   /mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/main.c 
	@${DEP_GEN} -d ${OBJECTDIR}/_ext/876597078/main.o 
	
${OBJECTDIR}/_ext/876597078/usb_descriptors.o: /mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/usb_descriptors.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/876597078 
	@${RM} ${OBJECTDIR}/_ext/876597078/usb_descriptors.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/_ext/876597078/usb_descriptors.o   /mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/usb_descriptors.c 
	@${DEP_GEN} -d ${OBJECTDIR}/_ext/876597078/usb_descriptors.o 
	
${OBJECTDIR}/src/usb_memory.o: src/usb_memory.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src 
	@${RM} ${OBJECTDIR}/src/usb_memory.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/usb_memory.o   src/usb_memory.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/usb_memory.o 
	
${OBJECTDIR}/src/Drivers/atflash.o: src/Drivers/atflash.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Drivers 
	@${RM} ${OBJECTDIR}/src/Drivers/atflash.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Drivers/atflash.o   src/Drivers/atflash.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Drivers/atflash.o 
	
${OBJECTDIR}/src/Drivers/SPI.o: src/Drivers/SPI.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Drivers 
	@${RM} ${OBJECTDIR}/src/Drivers/SPI.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Drivers/SPI.o   src/Drivers/SPI.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Drivers/SPI.o 
	
${OBJECTDIR}/src/Services/commands_flash.o: src/Services/commands_flash.c  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/src/Services 
	@${RM} ${OBJECTDIR}/src/Services/commands_flash.o.d 
	${MP_CC} $(MP_EXTRA_CC_PRE) -p$(MP_PROCESSOR_OPTION) -k -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip/Include" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Microchip" -I"/mnt/DATA/documents/UCB/WSN/openwsn/trunk/software/current_monitor.X/src/Services"  -I ${MP_CC_DIR}/../h  -fo ${OBJECTDIR}/src/Services/commands_flash.o   src/Services/commands_flash.c 
	@${DEP_GEN} -d ${OBJECTDIR}/src/Services/commands_flash.o 
	
endif

# ------------------------------------------------------------------------------------
# Rules for buildStep: link
ifeq ($(TYPE_IMAGE), DEBUG_RUN)
dist/${CND_CONF}/${IMAGE_TYPE}/current_monitor.X.${IMAGE_TYPE}.${OUTPUT_SUFFIX}: ${OBJECTFILES}  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} dist/${CND_CONF}/${IMAGE_TYPE} 
	${MP_LD} $(MP_EXTRA_LD_PRE)   -p$(MP_PROCESSOR_OPTION_LD)  -w -x -u_DEBUG   -z__MPLAB_BUILD=1  -u_CRUNTIME -z__MPLAB_DEBUG=1 -z__MPLAB_DEBUGGER_PK3=1 $(MP_LINKER_DEBUG_OPTION) -l ${MP_CC_DIR}/../lib  -o dist/${CND_CONF}/${IMAGE_TYPE}/current_monitor.X.${IMAGE_TYPE}.${OUTPUT_SUFFIX}  ${OBJECTFILES_QUOTED_IF_SPACED}   
else
dist/${CND_CONF}/${IMAGE_TYPE}/current_monitor.X.${IMAGE_TYPE}.${OUTPUT_SUFFIX}: ${OBJECTFILES}  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} dist/${CND_CONF}/${IMAGE_TYPE} 
	${MP_LD} $(MP_EXTRA_LD_PRE)   -p$(MP_PROCESSOR_OPTION_LD)  -w    -z__MPLAB_BUILD=1  -u_CRUNTIME -l ${MP_CC_DIR}/../lib  -o dist/${CND_CONF}/${IMAGE_TYPE}/current_monitor.X.${IMAGE_TYPE}.${DEBUGGABLE_SUFFIX}  ${OBJECTFILES_QUOTED_IF_SPACED}   
endif


# Subprojects
.build-subprojects:


# Subprojects
.clean-subprojects:

# Clean Targets
.clean-conf: ${CLEAN_SUBPROJECTS}
	${RM} -r build/default
	${RM} -r dist/default

# Enable dependency checking
.dep.inc: .depcheck-impl

DEPFILES=$(shell "${PATH_TO_IDE_BIN}"mplabwildcard ${POSSIBLE_DEPFILES})
ifneq (${DEPFILES},)
include ${DEPFILES}
endif
