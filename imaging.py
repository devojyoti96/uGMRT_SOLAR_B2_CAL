concat(vis=['sun_scan4_290_360_034910_035010.ms', 'sun_scan4_290_360_034020_034055.ms', 'sun_scan4_290_360_034342_034409.ms', 'sun_scan4_290_360_034515_034547.ms', 'sun_scan4_290_360_033700_033715.ms'],concatvis="sun_scan4_cal.ms",freqtol="",dirtol="",respectname=False,timesort=True,copypointing=True,visweightscale=[],forcesingleephemfield="")


gaincal(vis="sun_scan4_cal.ms",caltable="sun_scan4.gcalp",field="",spw="",intent="",selectdata=True,timerange="",uvrange=">0.8klambda",antenna="",scan="",observation="",msselect="",solint="1min",combine="",preavg=-1,refant="9",refantmode="flex",minblperant=4,minsnr=3.0,solnorm=False,normtype="mean",gaintype="G",smodel=[],calmode="p",solmode="L1R",rmsthresh=[10, 7, 5],corrdepflags=False,append=False,splinetime=3600.0,npointaver=3,phasewrap=180.0,docallib=False,callib="",gaintable=[],gainfield=[],interp=[],spwmap=[],parang=False)

applycal(vis="sun_scan4.ms",field="",spw="",intent="",selectdata=True,timerange="",uvrange="",antenna="",scan="",observation="",msselect="",docallib=False,callib="",gaintable=['sun_scan4.gcalp'],gainfield=[],interp=['linear'],spwmap=[],calwt=[True],parang=False,applymode="calonly",flagbackup=True)

