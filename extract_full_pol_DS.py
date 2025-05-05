from casatools import msmetadata,table,measures,quanta,agentflagger,image,calibrater,ms
from casatasks import *
import os,copy,numpy as np,matplotlib.pyplot as plt,sys
from optparse import OptionParser

def convert_lta_to_ms(lta_file,msname='',keepfits=False):
	'''
	Convert LTA file to ms
	Parameters
	----------
	lta_file : str
		Name of the lts file
	msname : str
		Name of the output measurement set (default : <lta_file_basename>.ms)
	keepfits : bool
		Keep fits file or not
	Returns
	-------
	str
		Name of the ms
	'''
	os.system('./listscan '+lta_file)
	lta_basename=lta_file.split('.')[0]
	gvfits_log=lta_basename+'.log'
	logfile=open(gvfits_log,'r')
	lines=logfile.readlines()
	for i in range(len(lines)):
		if 'SELF' in lines[i]:
			target_line=lines[i]
			split_list=target_line.split(' ')
			if '1' not in split_list:
				index=split_list.index('0')
				split_list[index]='1'
			target_line=' '.join(split_list)
			lines[i]=target_line
	logfile.close()
	os.system('rm -rf '+gvfits_log)
	logfile=open(gvfits_log,'a+')
	logfile.writelines(lines)
	logfile.seek(0)
	logfile.close()
	os.system('./gvfits '+gvfits_log)
	if msname=='':
		msname=lta_basename+'.ms'
	importuvfits(fitsfile='TEST.FITS',vis=msname)
	if keepfits:
		os.system('mv TEST.FITS '+lta_basename+'.fits')
	else:
		os.system('rm -rf TEST.FITS')
	return msname

def get_bad_channels(msname):
	'''
	Function to get bad channels of uGMRT band-2
	Parameters
	----------
	msname : str
		Name of the measurement set
	Return
	------
	str
		Bad channel spws in CASA format
	'''
	msmd=msmetadata()
	spw_freqlist=['100~130','165~190','250~300']
	spw='0:'
	msmd.open(msname)
	freqs=msmd.chanfreqs(0)/10**6 # In MHz
	msmd.close()
	for s in spw_freqlist:
		start_freq=int(s.split('~')[0])
		end_freq=int(s.split('~')[-1])
		start_chan=np.argmin(np.abs(freqs-start_freq))
		end_chan=np.argmin(np.abs(freqs-end_freq))
		x=np.min([start_chan,end_chan])
		y=np.max([start_chan,end_chan])
		spw+=str(x)+'~'+str(y)+';'	
	spw=spw[:-1]
	return spw

def get_good_channels(msname):
	'''
	Function to get good channels of uGMRT band-2
	Parameters
	----------
	msname : str
		Name of the measurement set
	Return
	------
	str
		Good channel spws in CASA format
	'''
	msmd=msmetadata()
	spw_freqlist=['217~219']
	spw='0:'
	msmd.open(msname)
	freqs=msmd.chanfreqs(0)/10**6 # In MHz
	msmd.close()
	for s in spw_freqlist:
		start_freq=int(s.split('~')[0])
		end_freq=int(s.split('~')[-1])
		start_chan=np.argmin(np.abs(freqs-start_freq))
		end_chan=np.argmin(np.abs(freqs-end_freq))
		x=np.min([start_chan,end_chan])
		y=np.max([start_chan,end_chan])
		spw+=str(x)+'~'+str(y)+';'	
	spw=spw[:-1]
	return spw

def flag_bad_chans(msname):
	'''
	Flag band-2 bad channels
	msnsame : str
		Name of the measurement set
	'''
	bad_spw=get_bad_channels(msname)
	print ('flagdata(vis=\''+msname+'\',mode=\'manual\',spw=\''+bad_spw+'\')')
	flagdata(vis=msname,mode='manual',spw=bad_spw)
	return

def get_bad_ants(msname):
	'''
	Function to get bad antennas
	'''
	good_channels=get_good_channels(msname)
	print ('Calculating statistics on channels : '+good_channels)
	bad_ants=[]
	msmd=msmetadata()
	msmd.open(msname)
	nant=msmd.nantennas()
	field_names=msmd.fieldnames()
	cal_field=''
	for field in field_names:
		if field=='3C48' or field=='3C147' or field=='3C286' or field=='3C138' or field=='3C84':
			cal_field=field
			break
	msmd.close()
	for ant in range(nant):
		for pol in ['RR','LL']:
			try:
				median=visstat(vis=msname,antenna=str(ant),correlation=pol,field=cal_field,spw=good_channels,uvrange='>0lambda')['DATA_DESC_ID=0']['median']
				if median<=0.2:
					if ant not in bad_ants:
						print ('Bad antenna found. Antenna : '+str(ant)+'\n')
						bad_ants.append(ant)
			except:
				pass
	return bad_ants

def flag_bad_ants(msname):
	'''
	Flag bad antennas
	'''
	bad_ant_list=get_bad_ants(msname)
	bad_ants=''
	for ant in bad_ant_list:
		bad_ants+=str(ant)+','
	bad_ants=bad_ants[:-1]
	print ('flagdata(vis=\''+msname+'\',mode=\'manual\',antenna=\''+bad_ants+'\')\n')
	flagdata(vis=msname,mode='manual',antenna=bad_ants)
	return

def get_stokes_ds(msname,ant1,ant2,field=None):
	'''
	Full stokes dynamic spectrum for a baseline
	Parameters
	----------
	msname : str
		Name of the measurement set
	ant1 : int
		First antenna index
	ant2 : int
		Second antenna index
	field : int
		Field id
	Returns
	-------
	numpy.array
		Dynamic spectra of normalised cross-correlation
	'''
#	casalog.showconsole(True)
	msdata=ms()
	msdata.open(msname)
	if field!=None:
		msdata.select({'antenna1':ant1,'antenna2':ant2,'field_id':int(field)})
	else:
		msdata.select({'antenna1':ant1,'antenna2':ant2})
	print ('Extracting cross correations.\n')
	data_cross=msdata.getdata('DATA',ifraxis=True)['data']
	flag_cross=msdata.getdata('FLAG',ifraxis=True)['flag']
	#data_cross[flag_cross]=np.nan
	msdata.close()
	# Antenna 1 auto-correlation
	msdata.open(msname)
	if field!=None:
		msdata.select({'antenna1':ant1,'antenna2':ant1,'field_id':int(field)})
	else:
		msdata.select({'antenna1':ant1,'antenna2':ant1})
	print ('Extracting auto-correations for antenna 1.\n')
	data_autocorr1=msdata.getdata('DATA',ifraxis=True)['data']
	flag_autocorr1=msdata.getdata('FLAG',ifraxis=True)['flag']
	#data_autocorr1[flag_autocorr1]=np.nan
	msdata.close()
	# Antenna 2 auto-correlation
	msdata.open(msname)
	if field!=None:
		msdata.select({'antenna1':ant2,'antenna2':ant2,'field_id':int(field)})
	else:
		msdata.select({'antenna1':ant2,'antenna2':ant2})
	print ('Extracting auto-correations for antenna 2.\n')
	data_autocorr2=msdata.getdata('DATA',ifraxis=True)['data']
	flag_autocorr2=msdata.getdata('FLAG',ifraxis=True)['flag']
	#data_autocorr2[flag_autocorr2]=np.nan
	msdata.close()
	rr1_autocorr=data_autocorr1[0,:,0,:]
	ll1_autocorr=data_autocorr1[3,:,0,:]
	rr2_autocorr=data_autocorr2[0,:,0,:]
	ll2_autocorr=data_autocorr2[3,:,0,:]
	#r_N=data_cross/np.sqrt(data_autocorr1*data_autocorr2)
	data_cross=data_cross[:,:,0,:]
	rr=data_cross[0,...]/np.sqrt(rr1_autocorr*rr2_autocorr)
	rl=data_cross[1,...]/np.sqrt(rr1_autocorr*ll2_autocorr)
	lr=data_cross[2,...]/np.sqrt(ll1_autocorr*rr2_autocorr)
	ll=data_cross[3,...]/np.sqrt(ll1_autocorr*ll2_autocorr)
	I=np.abs((rr+ll)/2.0)
	V=np.abs((rr-ll)/2.0)
	Q=(np.real(rl)+np.real(lr))/2.0
	U=(np.imag(rl)+np.imag(lr))/2.0
	p=np.sqrt(Q**2+U**2)
	print (I.shape,flag_cross.shape)
	'''I[flag_cross[0,:,0,:]]=np.nan
	Q[flag_cross[0,:,0,:]]=np.nan
	U[flag_cross[0,:,0,:]]=np.nan
	V[flag_cross[0,:,0,:]]=np.nan
	p[flag_cross[0,:,0,:]]=np.nan'''
	return I,Q,U,V,p
	
	
def perform_flag(msname):
	'''
	Function to perform basic flagging
	Parameters
	----------
	msname : str
		Name of the measurement set
	'''
	print ('Flagging bad channels.\n')
	flag_bad_chans(msname)
	'''print ('Flagging quack times.\n')
	print ('flagdata(vis=\''+msname+'\',mode=\'quack\',quackinterval=10.0,quackmode=\'beg\')')
	flagdata(vis=msname,mode='quack',quackinterval=10.0,quackmode='beg')
	print ('flagdata(vis=\''+msname+'\',mode=\'quack\',quackinterval=10.0,quackmode=\'endb\')')
	flagdata(vis=msname,mode='quack',quackinterval=10.0,quackmode='endb')'''
	print ('Flagging bad antennas.\n')
	flag_bad_ants(msname)
	return


# Inputs
########
def main():
	usage= 'Make uGMRT band-2 dynamic spectrum from visibilities for the Sun'
	parser = OptionParser(usage=usage)
	parser.add_option('--lta_file',dest="lta_file",default=None,help="Name of LTA file",metavar="LTA file")
	parser.add_option('--msname',dest="msname",default=None,help="Name of measurement set",metavar="Measurement Set")
	(options, args) = parser.parse_args()
		
	if options.lta_file==None and options.msname==None:
		print ('Please provide either the name of the LTA file or measurement set.\n')
		return 1
	elif options.lta_file!=None:
		if os.path.exists(options.lta_file):
			msname=convert_lta_to_ms(options.lta_file,msname='',keepfits=False)
		else:
			print ('Given LTA file does not exist.\n')
			return 1
	else:
		if os.path.exists(options.msname):
			msname=options.msname
		else:
			print ('Given measurement set does not exist.\n')
			return 1
		perform_flag(options.msname)
		msmd=msmetadata()
		msmd.open(options.msname)
		fields=msmd.fieldnames()
		msmd.close()
			


if __name__=='__main__':
	success=main()
	os._exit(success)






































