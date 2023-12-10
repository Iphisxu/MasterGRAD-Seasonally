      PROGRAM create_emis

      IMPLICIT NONE

!...  INCLUDES:
      INCLUDE 'PARMS3.EXT'        !  I/O API parameters
      INCLUDE 'IODECL3.EXT'       !  I/O API function declarations
      INCLUDE 'FDESC3.EXT'        !  I/O API file description data structures.

!...........   EXTERNAL FUNCTIONS and their descriptions:
      LOGICAL      DSCGRID
      EXTERNAL     DSCGRID
      INTEGER, EXTERNAL :: ENVINT, WKDAY, JULIAN

!... Program I/O files
! Program name
      CHARACTER(len=16)  :: PROGNAME  = 'LIUEMIS'
! input file
      CHARACTER(len=16) :: POW_FILE = 'POW_FILE'
      CHARACTER(len=16) :: IND_FILE = 'IND_FILE'
      CHARACTER(len=16) :: RES_FILE = 'RES_FILE'
      CHARACTER(len=16) :: TRA_FILE = 'TRA_FILE'
      CHARACTER(len=16) :: AGR_FILE = 'AGR_FILE'
      CHARACTER(len=16) :: BIO_FILE = 'BIO_FILE'
      CHARACTER(len=16) :: SHP_FILE = 'SHP_FILE'
      CHARACTER(len=16) :: OTH_FILE = 'OTH_FILE'
      CHARACTER(len=16) :: EPD_FILE = 'EPD_FILE'
      CHARACTER(len=16) :: MAS_FILE = 'MAS_FILE'
! Output file
      CHARACTER(len=16) :: EMIS_1     = 'EMIS_1'
! Parameters for file units
      INTEGER :: logdev

! I/O API file parameters
      INTEGER       jdate          ! Looping date YYYYDDD
      INTEGER       jtime          ! Looping time HHMMSS
!      INTEGER       ncols          ! Number of columns
!      INTEGER       nrows          ! Number of rows
!      INTEGER       mxrec          ! Total number of time steps
      INTEGER       sdate          ! Start date YYYYDDD
      INTEGER       stime          ! Start time HHMMSS
      INTEGER       tstep          ! Time step
      INTEGER       bdate          ! for read EPD emission file

! I/O API file parameters for reading emission file
      INTEGER       rdjdate
      INTEGER       rdjtime
      INTEGER       rdtstep

!... Internal parameters
! internal paramters (status and buffer)
      INTEGER   ios                               ! i/o status
      CHARACTER(len=256) :: MESG                  ! Message buffer

! local variables and their descriptions:
!     CHARACTER(len=16)  :: GDNAM
      CHARACTER(len=16)  :: CNAME
! Count number: t for time and s for variable(variables)
      INTEGER :: t,s,z,i,j
! Current date: year, month, day, week and the first day of week
      INTEGER :: YEAR, MONTH, DAY, WEEK, WEEK_FIRST
! number of days in week and number of days in month
      INTEGER :: WEEK_NUM(7),MON_NUM(12)
! Week factor of POWER, INDUSTRY, RESIDENTIAL and TRANSPORT
      REAL :: week_fac_pow(7),week_fac_ind(7)
      REAL :: week_fac_res(7),week_fac_tra(7)
      REAL :: week_fac_shp(7)
! Hourly factor of POWER, INDUSTRY, RESIDENTIAL and TRANSPORT
      REAL :: hour_fac_pow(25),hour_fac_ind(25)
      REAL :: hour_fac_res(25),hour_fac_tra(25)
      REAL :: hour_fac_agr(25),hour_fac_shp(25)
! Vertical factor of POWER, INDUSTRY, RESIDENTIAL and TRANSPORT 
      REAL :: vert_fac_pow(26),vert_fac_ind(26)
      REAL :: vert_fac_res(26),vert_fac_tra(26)
      REAL :: vert_fac_agr(26),vert_fac_bio(26)
      REAL :: vert_fac_shp(26),vert_fac_oth(26)
! Day factor of POWER, INDUSTRY, RESIDENTIAL and TRANSPORT
      REAL :: day_fac_pow, day_fac_ind
      REAL :: day_fac_res, day_fac_tra, day_fac_shp
! Variables list in input nc file
      CHARACTER(len=16)  :: GCVARLIST(54), AEVARLIST(19)
      CHARACTER(len=16)  :: NRVARLIST(1),  BIOVARLIST(31)
      CHARACTER(len=16)  :: EPDVARLIST(34)
! Variables index from input file to output file
      INTEGER :: ant_index(74), agr_index(1)
      INTEGER :: bio_index(31),oth_index(2)
! emission data from input file
      REAL, ALLOCATABLE, DIMENSION (:,:,:,:) :: VAR_POW, VAR_IND
      REAL, ALLOCATABLE, DIMENSION (:,:,:,:) :: VAR_TRA, VAR_RES
      REAL, ALLOCATABLE, DIMENSION (:,:,:,:) :: VAR_BIO, VAR_SHP
      REAL, ALLOCATABLE, DIMENSION (:,:,:,:) :: VAR_AGR, VAR_OTH
      REAL, ALLOCATABLE, DIMENSION (:,:,:,:,:) :: VAR_EPD
! emission data IBUFF(NCOL,NROW,LAYER,TIME,VAR)
      REAL,ALLOCATABLE :: IBUFF(:,:,:,:,:),tmpBUFF(:,:,:,:,:) 
! mask file data
      INTEGER, ALLOCATABLE, DIMENSION (:,:) :: MASK

! temporary number
      INTEGER :: tmpint

!***********************************************************************

!=======================================================================
!...  Begin program
!=======================================================================


!-----------------------------------------------------------------------
!.....1) File set up and assign I/O parameters
!-----------------------------------------------------------------------
!... Get input parameters from run script
      logdev = init3()

      CALL ENVSTR( 'GRID_NAME', MESG, 'LIU', GDNAM3D, IOS )
      IF( .NOT. DSCGRID( GDNAM3D, CNAME, GDTYP3D,
     &              P_ALP3D, P_BET3D, P_GAM3D, XCENT3D, YCENT3D,
     &              XORIG3D, YORIG3D, XCELL3D, YCELL3D,
     &              NCOLS3D, NROWS3D, NTHIK3D ) ) THEN
         MESG = 'Could not get grid description.'
         CALL M3EXIT ( PROGNAME, 0, 0, MESG, 2 )
      ENDIF

!... Get today's date
      sdate = ENVINT( 'STDATE', MESG, 0, ios )
      sdate = sdate - 62 ! convert 0901 to 0701 -- by Evan
      stime = 0
      tstep = 10000
      jdate = sdate
      jtime = stime

!... Get EPD emission day's date
      bdate = ENVINT( 'BSDATE', MESG, 0, ios )
      ! bdate = bdate - 62 ! convert 0901 to 0701 -- by Evan

!      write(*,*)GDNAM,CNAME,GDTYP3D,P_ALP3D,P_BET3D,P_GAM3D,XCENT3D,
!     &               YCENT3D,XORIG3D,YORIG3D,XCELL3D,YCELL3D,NCOLS3D,
!     &               NROWS3D,NTHIK3D


!-----------------------------------------------------------------------
!.....2) Compute the temporal and verticle factors
!-----------------------------------------------------------------------
!... Load data set
      mon_num=(/31,28,31,30,31,30,31,31,30,31,30,31/)

      week_fac_pow=(/0.154,0.154,0.154,0.154,0.154,0.115,0.115/)
      week_fac_ind=(/0.159,0.159,0.159,0.159,0.159,0.103,0.103/)
      week_fac_res=(/0.159,0.159,0.159,0.159,0.159,0.103,0.103/)
      week_fac_tra=(/0.154,0.154,0.154,0.154,0.154,0.115,0.115/)
      week_fac_shp=(/0.154,0.154,0.154,0.154,0.154,0.115,0.115/)

      hour_fac_pow=(/0.0433,0.0457,0.0478,0.0486,0.0494,0.0497,0.0501,
     &               0.0500,0.0497,0.0489,0.0477,0.0473,0.0466,0.0440,
     &               0.0397,0.0353,0.0325,0.0300,0.0288,0.0284,0.0292,
     &               0.0316,0.0354,0.0403,0.0433/)
      hour_fac_ind=(/0.0450,0.0680,0.0680,0.0680,0.0680,0.0680,0.0680,
     &               0.0680,0.0680,0.0660,0.0630,0.0370,0.0370,0.0370,
     &               0.0370,0.0370,0.0260,0.0070,0.0070,0.0070,0.0070,
     &               0.0070,0.0070,0.0290,0.0450/)
      hour_fac_res=(/0.0380,0.0380,0.0300,0.0450,0.0450,0.0380,0.0300,
     &               0.0300,0.0380,0.0750,0.0750,0.0750,0.0750,0.0540,
     &               0.0180,0.0180,0.0180,0.0180,0.0180,0.0180,0.0180,
     &               0.0380,0.0750,0.0750,0.0380/)
      hour_fac_tra=(/0.0599,0.0590,0.0594,0.0540,0.0501,0.0587,0.0600,
     &               0.0620,0.0594,0.0574,0.0557,0.0490,0.0454,0.0417,
     &               0.0308,0.0216,0.0173,0.0132,0.0138,0.0150,0.0155,
     &               0.0157,0.0290,0.0564,0.0599/)
      hour_fac_agr=(/0.0285,0.0485,0.0681,0.0853,0.0986,0.1051,0.1037,
     &               0.0934,0.0755,0.0525,0.0307,0.0213,0.0193,0.0180,
     &               0.0171,0.0164,0.0158,0.0153,0.0149,0.0145,0.0142,
     &               0.0139,0.0136,0.0158,0.0285/)
      hour_fac_shp=(/0.0599,0.0590,0.0594,0.0540,0.0501,0.0587,0.0600,
     &               0.0620,0.0594,0.0574,0.0557,0.0490,0.0454,0.0417,
     &               0.0308,0.0216,0.0173,0.0132,0.0138,0.0150,0.0155,
     &               0.0157,0.0290,0.0564,0.0599/)

      vert_fac_pow=(/0.00,0.00,0.00,0.00,0.05,0.05,0.05,0.05,0.15,0.15,
     &               0.10,0.10,0.10,0.10,0.05,0.05,0,0,0,0,0,0,0,0,0,0/)
      vert_fac_ind=(/0.30,0.20,0.10,0.10,0.10,0.10,0.10,0.00,0,0,0,0,0,
     &               0,0,0,0,0,0,0,0,0,0,0,0,0/)
      vert_fac_res=(/1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0/)
      vert_fac_tra=(/1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0/)
      vert_fac_agr=(/1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0/)
      vert_fac_shp=(/1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0/)
      vert_fac_bio=(/1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0/)
      vert_fac_oth=(/1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0/)

      print*,'print sum of factors'
      print*,sum(week_fac_pow),sum(week_fac_ind),sum(week_fac_res),
     &       sum(week_fac_tra),sum(hour_fac_pow),sum(hour_fac_ind),
     &       sum(hour_fac_res),sum(hour_fac_tra),sum(hour_fac_agr),
     &       sum(vert_fac_pow),sum(vert_fac_ind),sum(vert_fac_res),
     &       sum(vert_fac_tra),sum(vert_fac_agr),sum(vert_fac_bio),
     &       sum(vert_fac_oth)

!... Get date and time
      YEAR = jdate/1000
      CALL DAYMON( jdate, MONTH, DAY ) 
      WEEK = WKDAY( jdate )
      WEEK_FIRST = WKDAY( YEAR*1000+JULIAN(YEAR, MONTH, 1) )

!... if this is a leap year
      if ( ( MOD(YEAR,4)==0 .and. MOD(YEAR,100)/=0 ) .or.
     &                          MOD(YEAR,400)==0 ) then
        MON_NUM(2)=29
      end if

!... Calculate the number of week in this month
      WEEK_NUM(:)=4
      if ( MON_NUM( MONTH ) /= 28 ) then
        do t=WEEK_FIRST,WEEK_FIRST+MON_NUM( MONTH )-29
          tmpint=MOD(t,7)
          if (tmpint==0) tmpint=7
          WEEK_NUM( tmpint )=WEEK_NUM( tmpint )+1
        end do
      endif

!... Calculate the factor today
      day_fac_pow = week_fac_pow( WEEK )/SUM( WEEK_NUM*week_fac_pow )
      day_fac_ind = week_fac_ind( WEEK )/SUM( WEEK_NUM*week_fac_ind )
      day_fac_res = week_fac_res( WEEK )/SUM( WEEK_NUM*week_fac_res )
      day_fac_tra = week_fac_tra( WEEK )/SUM( WEEK_NUM*week_fac_tra )
      day_fac_shp = week_fac_shp( WEEK )/SUM( WEEK_NUM*week_fac_shp )

!      print*, day_fac_pow, day_fac_ind, day_fac_res, day_fac_tra


!-----------------------------------------------------------------------
!.....3) Get the data from input file
!-----------------------------------------------------------------------
!... Allocate the data from input file
      ALLOCATE ( VAR_POW( NCOLS3D, NROWS3D,  2, 12 ) )
      ALLOCATE ( VAR_IND( NCOLS3D, NROWS3D,  2, 12 ) )
      ALLOCATE ( VAR_RES( NCOLS3D, NROWS3D,  2, 12 ) )
!      ALLOCATE ( VAR_TRA( NCOLS3D, NROWS3D, 74, 12 ) )
!      ALLOCATE ( VAR_SHP( NCOLS3D, NROWS3D, 74, 12 ) )
!      ALLOCATE ( VAR_AGR( NCOLS3D, NROWS3D,  1, 12 ) )
      ALLOCATE ( VAR_BIO( NCOLS3D, NROWS3D, 31, 25 ) )
      ALLOCATE ( VAR_OTH( NCOLS3D, NROWS3D,  2, 12 ) )
      ALLOCATE ( VAR_EPD( NCOLS3D, NROWS3D, 26, 34, 25 ) )
      ALLOCATE ( MASK(NCOLS3D, NROWS3D) )

!... Load varaible index from input file to output file
      ant_index = (/1:6,74,40:44,27,28,46,47,29,30,31,51,52,33,34,48,
     &            36,35,37,38,49,32,7,14,15,23,12,16,18,8,39,17,9,10,
     &                  21,19,22,13,26,24,25,20,11,50,45,55:73,54,53/)
      agr_index = (/74/)
      bio_index = (/30,51,8,12,2,1,74,14,17,7,9,23,16,10,4,27,40,41,42,
     &             43,44,48,49,46,47,15,28,31,34,50,52/)
      oth_index = (/54,53/)

!... open input file
      IF ( .NOT. OPEN3( POW_FILE, FSREAD3, PROGNAME ) ) THEN
         CALL NAMEVAL (POW_FILE, MESG)  ! get input file name and path
         MESG = 'Could not open file '//TRIM(MESG)
         CALL M3EXIT( PROGNAME, 0, 0, MESG, 2 )
      ENDIF
      IF ( .NOT. OPEN3( IND_FILE, FSREAD3, PROGNAME ) ) THEN
         CALL NAMEVAL (IND_FILE, MESG)  ! get input file name and path
         MESG = 'Could not open file '//TRIM(MESG)
         CALL M3EXIT( PROGNAME, 0, 0, MESG, 2 )
      ENDIF
      IF ( .NOT. OPEN3( RES_FILE, FSREAD3, PROGNAME ) ) THEN
         CALL NAMEVAL (RES_FILE, MESG)  ! get input file name and path
         MESG = 'Could not open file '//TRIM(MESG)
         CALL M3EXIT( PROGNAME, 0, 0, MESG, 2 )
      ENDIF
!      IF ( .NOT. OPEN3( TRA_FILE, FSREAD3, PROGNAME ) ) THEN
!         CALL NAMEVAL (TRA_FILE, MESG)  ! get input file name and path
!         MESG = 'Could not open file '//TRIM(MESG)
!         CALL M3EXIT( PROGNAME, 0, 0, MESG, 2 )
!      ENDIF
!      IF ( .NOT. OPEN3( SHP_FILE, FSREAD3, PROGNAME ) ) THEN
!         CALL NAMEVAL (SHP_FILE, MESG)  ! get input file name and path
!         MESG = 'Could not open file '//TRIM(MESG)
!         CALL M3EXIT( PROGNAME, 0, 0, MESG, 2 )
!      ENDIF
!      IF ( .NOT. OPEN3( AGR_FILE, FSREAD3, PROGNAME ) ) THEN
!         CALL NAMEVAL (AGR_FILE, MESG)  ! get input file name and path
!         MESG = 'Could not open file '//TRIM(MESG)
!         CALL M3EXIT( PROGNAME, 0, 0, MESG, 2 )
!      ENDIF
      IF ( .NOT. OPEN3( OTH_FILE, FSREAD3, PROGNAME ) ) THEN
         CALL NAMEVAL (OTH_FILE, MESG)  ! get input file name and path
         MESG = 'Could not open file '//TRIM(MESG)
         CALL M3EXIT( PROGNAME, 0, 0, MESG, 2 )
      ENDIF
      IF ( .NOT. OPEN3( EPD_FILE, FSREAD3, PROGNAME ) ) THEN
         CALL NAMEVAL (EPD_FILE, MESG)  ! get input file name and path
         MESG = 'Could not open file '//TRIM(MESG)
         CALL M3EXIT( PROGNAME, 0, 0, MESG, 2 )
      ENDIF
      IF ( .NOT. OPEN3( BIO_FILE, FSREAD3, PROGNAME ) ) THEN
         CALL NAMEVAL (BIO_FILE, MESG)  ! get input file name and path
         MESG = 'Could not open file '//TRIM(MESG)
         CALL M3EXIT( PROGNAME, 0, 0, MESG, 2 )
      ENDIF
      IF ( .NOT. OPEN3( MAS_FILE, FSREAD3, PROGNAME ) ) THEN
         CALL NAMEVAL (MAS_FILE, MESG)  ! get input file name and path
         MESG = 'Could not open file '//TRIM(MESG)
         CALL M3EXIT( PROGNAME, 0, 0, MESG, 2 )
      ENDIF

      print*,"liu1" 
!... read input file
      rdjdate = 2010001
      rdjtime = 0
      rdtstep = 10000
      DO t=1,12
        IF( .NOT. READ3(POW_FILE,'ALL',-1,rdjdate,rdjtime,
     &                                        VAR_POW(:,:,:,t))) THEN
            MESG = 'Error reading '//TRIM(POW_FILE)
            CALL M3EXIT(PROGNAME,0,0,MESG,2)
        ENDIF
        print*,"liu2"
        IF( .NOT. READ3(IND_FILE,'ALL',-1,rdjdate,rdjtime,
     &                                        VAR_IND(:,:,:,t))) THEN
            MESG = 'Error reading '//TRIM(IND_FILE)
            CALL M3EXIT(PROGNAME,0,0,MESG,2)
        ENDIF
        IF( .NOT. READ3(RES_FILE,'ALL',-1,rdjdate,rdjtime,
     &                                        VAR_RES(:,:,:,t))) THEN
            MESG = 'Error reading '//TRIM(RES_FILE)
            CALL M3EXIT(PROGNAME,0,0,MESG,2)
        ENDIF
!        IF( .NOT. READ3(TRA_FILE,'ALL',-1,rdjdate,rdjtime,
!     &                                        VAR_TRA(:,:,:,t))) THEN
!            MESG = 'Error reading '//TRIM(TRA_FILE)
!            CALL M3EXIT(PROGNAME,0,0,MESG,2)
!        ENDIF
!        IF( .NOT. READ3(SHP_FILE,'ALL',-1,rdjdate,rdjtime,
!     &                                        VAR_SHP(:,:,:,t))) THEN
!            MESG = 'Error reading '//TRIM(SHP_FILE)
!            CALL M3EXIT(PROGNAME,0,0,MESG,2)
!        ENDIF
!        IF( .NOT. READ3(AGR_FILE,'ALL',-1,rdjdate,rdjtime,
!     &                                        VAR_AGR(:,:,:,t))) THEN
!            MESG = 'Error reading '//TRIM(AGR_FILE)
!            CALL M3EXIT(PROGNAME,0,0,MESG,2)
!        ENDIF
        IF( .NOT. READ3(OTH_FILE,'ALL',-1,rdjdate,rdjtime,
     &                                        VAR_OTH(:,:,:,t))) THEN
            MESG = 'Error reading '//TRIM(OTH_FILE)
            CALL M3EXIT(PROGNAME,0,0,MESG,2)
        ENDIF
        CALL NEXTIME(rdjdate,rdjtime,rdtstep)
      ENDDO

!... read MASK file
        IF( .NOT. READ3(MAS_FILE,'MASK',1,1,1,MASK)) THEN
            MESG = 'Error reading '//TRIM(MAS_FILE)
            CALL M3EXIT(PROGNAME,0,0,MESG,2)
        ENDIF

!... EPD CB05 emission variables lists
!....                 1        2         3          4         5
      EPDVARLIST = (/'ALD2',  'ALDX',   'BENZENE', 'CH4',    'CO',
!....                 6        7         8          9         10
     &               'ETH',   'ETHA',   'ETOH',    'FORM',   'HONO',
!....                 11       12        13         14        15
     &               'IOLE',  'ISOP',   'MEOH',    'NH3',    'NO',
!....                 16       17        18         19        20
     &               'NO2',   'NR',     'NROG',    'NVOL',   'OLE',
!....                 21       22        23         24        25
     &               'PAR',   'PEC',    'PMC',     'PMFINE', 'PNO3',
!....                 26       27        28         29        30
     &               'POA',   'PSO4',   'SO2',     'SULF',   'TERP',
!....                 31       32        33         34     
     &               'TOL',   'UNK',    'UNR',     'XYL'/)

      print*,"liu2"
!... read EPD emission input file
      rdjdate = bdate
      rdjtime = 0
      rdtstep = 10000
      DO t=1,25
        DO s=1,34
          IF( .NOT. READ3(EPD_FILE,EPDVARLIST(s),-1,rdjdate,rdjtime,
     &                                        VAR_EPD(:,:,:,s,t))) THEN
            MESG = 'Error reading '//TRIM(EPD_FILE)
            CALL M3EXIT(PROGNAME,0,0,MESG,2)
          ENDIF
        ENDDO
        CALL NEXTIME(rdjdate,rdjtime,rdtstep)
      ENDDO

!... Control the anthropogenic emission EPD
      DO i=1,NCOLS3D
        DO j=1,NROWS3D
          SELECT CASE (MASK(i,j))
!====================================================================
          CASE (1) ! China except Guangdong
!... NOx
            VAR_EPD(i,j,:,10,:) = VAR_EPD(i,j,:,10,:)*0.952
            VAR_EPD(i,j,:,15,:) = VAR_EPD(i,j,:,15,:)*0.952
            VAR_EPD(i,j,:,16,:) = VAR_EPD(i,j,:,16,:)*0.952
!... SO2
            VAR_EPD(i,j,:,28:29,:) = VAR_EPD(i,j,:,28:29,:)*0.803
!... CO
            VAR_EPD(i,j,:,5,:) = VAR_EPD(i,j,:,5,:)*0.944
!... NH3
            VAR_EPD(i,j,:,14,:) = VAR_EPD(i,j,:,14,:)*0.873
!... VOC
            VAR_EPD(i,j,:,1:3,:) = VAR_EPD(i,j,:,1:3,:)*0.945
            VAR_EPD(i,j,:,6:9,:) = VAR_EPD(i,j,:,6:9,:)*0.945
            VAR_EPD(i,j,:,11:13,:) = VAR_EPD(i,j,:,11:13,:)*0.945
            VAR_EPD(i,j,:,17:21,:) = VAR_EPD(i,j,:,17:21,:)*0.945
            VAR_EPD(i,j,:,30:34,:) = VAR_EPD(i,j,:,30:34,:)*0.945
!... EC
            VAR_EPD(i,j,:,22,:) = VAR_EPD(i,j,:,22,:)*0.826
!... OC
            VAR_EPD(i,j,:,26,:) = VAR_EPD(i,j,:,26,:)*0.920
!... PM2.5
            VAR_EPD(i,j,:,24:25,:) = VAR_EPD(i,j,:,24:25,:)*0.839
            VAR_EPD(i,j,:,27,:) = VAR_EPD(i,j,:,27,:)*0.839
!... PMC
            VAR_EPD(i,j,:,23,:) = VAR_EPD(i,j,:,23,:)*0.839
!====================================================================
          CASE (2) ! Guangdong
!... NOx
            VAR_EPD(i,j,:,10,:) = VAR_EPD(i,j,:,10,:)*0.963
            VAR_EPD(i,j,:,15,:) = VAR_EPD(i,j,:,15,:)*0.963
            VAR_EPD(i,j,:,16,:) = VAR_EPD(i,j,:,16,:)*0.963
!... SO2
            VAR_EPD(i,j,:,28:29,:) = VAR_EPD(i,j,:,28:29,:)*0.671
!... CO
            VAR_EPD(i,j,:,5,:) = VAR_EPD(i,j,:,5,:)*0.901
!... NH3
            VAR_EPD(i,j,:,14,:) = VAR_EPD(i,j,:,14,:)*0.869
!... VOC
            VAR_EPD(i,j,:,1:3,:) = VAR_EPD(i,j,:,1:3,:)*1.023
            VAR_EPD(i,j,:,6:9,:) = VAR_EPD(i,j,:,6:9,:)*1.023
            VAR_EPD(i,j,:,11:13,:) = VAR_EPD(i,j,:,11:13,:)*1.023
            VAR_EPD(i,j,:,17:21,:) = VAR_EPD(i,j,:,17:21,:)*1.023
            VAR_EPD(i,j,:,30:34,:) = VAR_EPD(i,j,:,30:34,:)*1.023
!... EC
            VAR_EPD(i,j,:,22,:) = VAR_EPD(i,j,:,22,:)*0.851
!... OC
            VAR_EPD(i,j,:,26,:) = VAR_EPD(i,j,:,26,:)*0.929
!... PM2.5
            VAR_EPD(i,j,:,24:25,:) = VAR_EPD(i,j,:,24:25,:)*0.824
            VAR_EPD(i,j,:,27,:) = VAR_EPD(i,j,:,27,:)*0.824
!... PMC
            VAR_EPD(i,j,:,23,:) = VAR_EPD(i,j,:,23,:)*0.824
!====================================================================
          CASE (3) ! Hong Kong
!... NOx
            VAR_EPD(i,j,:,10,:) = VAR_EPD(i,j,:,10,:)*0.927
            VAR_EPD(i,j,:,15,:) = VAR_EPD(i,j,:,15,:)*0.927
            VAR_EPD(i,j,:,16,:) = VAR_EPD(i,j,:,16,:)*0.927
!... SO2
            VAR_EPD(i,j,:,28:29,:) = VAR_EPD(i,j,:,28:29,:)*0.522
!... CO
            VAR_EPD(i,j,:,5,:) = VAR_EPD(i,j,:,5,:)*1.049
!... NH3
            VAR_EPD(i,j,:,14,:) = VAR_EPD(i,j,:,14,:)*1.0
!... VOC
            VAR_EPD(i,j,:,1:3,:) = VAR_EPD(i,j,:,1:3,:)*0.883
            VAR_EPD(i,j,:,6:9,:) = VAR_EPD(i,j,:,6:9,:)*0.883
            VAR_EPD(i,j,:,11:13,:) = VAR_EPD(i,j,:,11:13,:)*0.883
            VAR_EPD(i,j,:,17:21,:) = VAR_EPD(i,j,:,17:21,:)*0.883
            VAR_EPD(i,j,:,30:34,:) = VAR_EPD(i,j,:,30:34,:)*0.883
!... EC
            VAR_EPD(i,j,:,22,:) = VAR_EPD(i,j,:,22,:)*0.822
!... OC
            VAR_EPD(i,j,:,26,:) = VAR_EPD(i,j,:,26,:)*0.822
!... PM2.5
            VAR_EPD(i,j,:,24:25,:) = VAR_EPD(i,j,:,24:25,:)*0.822
            VAR_EPD(i,j,:,27,:) = VAR_EPD(i,j,:,27,:)*0.822
!... PMC
            VAR_EPD(i,j,:,23,:) = VAR_EPD(i,j,:,23,:)*0.966
!====================================================================
          CASE DEFAULT
!... NOx
            VAR_EPD(i,j,:,10,:) = VAR_EPD(i,j,:,10,:)*1.0
            VAR_EPD(i,j,:,15,:) = VAR_EPD(i,j,:,15,:)*1.0
            VAR_EPD(i,j,:,16,:) = VAR_EPD(i,j,:,16,:)*1.0
!... SO2
            VAR_EPD(i,j,:,28:29,:) = VAR_EPD(i,j,:,28:29,:)*1.0
!... CO
            VAR_EPD(i,j,:,5,:) = VAR_EPD(i,j,:,5,:)*1.0
!... NH3
            VAR_EPD(i,j,:,14,:) = VAR_EPD(i,j,:,14,:)*1.0
!... VOC
            VAR_EPD(i,j,:,1:3,:) = VAR_EPD(i,j,:,1:3,:)*1.0
            VAR_EPD(i,j,:,6:9,:) = VAR_EPD(i,j,:,6:9,:)*1.0
            VAR_EPD(i,j,:,11:13,:) = VAR_EPD(i,j,:,11:13,:)*1.0
            VAR_EPD(i,j,:,17:21,:) = VAR_EPD(i,j,:,17:21,:)*1.0
            VAR_EPD(i,j,:,30:34,:) = VAR_EPD(i,j,:,30:34,:)*1.0
!... EC
            VAR_EPD(i,j,:,22,:) = VAR_EPD(i,j,:,22,:)*1.0
!... OC
            VAR_EPD(i,j,:,26,:) = VAR_EPD(i,j,:,26,:)*1.0
!... PM2.5
            VAR_EPD(i,j,:,24:25,:) = VAR_EPD(i,j,:,24:25,:)*1.0
            VAR_EPD(i,j,:,27,:) = VAR_EPD(i,j,:,27,:)*1.0
!... PMC
            VAR_EPD(i,j,:,23,:) = VAR_EPD(i,j,:,23,:)*1.0
          END SELECT
        ENDDO
      ENDDO


!... Biogenic emission variables lists
      BIOVARLIST = (/'ISOP','TERP','MEOH','ACET','NO','NO2','NH3',
     &               'CCHO','FACD','HCHO','AACD','BALD','MEK','PACD',
     &               'CO','ETHE','ALK1','ALK2','ALK3','ALK4','ALK5',
     &               'ARO1','ARO2MN','OLE1','OLE2','RCHO','PRPE',
     &               'APIN','TOLU','NAPH','SESQ'/)
      DO t=1,25
        DO s=1,31
          IF( .NOT. READ3(BIO_FILE,BIOVARLIST(s),-1,jdate,jtime,
     &                                       VAR_BIO(:,:,s,t))) THEN
            MESG = 'Error reading '//TRIM(BIO_FILE)
            CALL M3EXIT(PROGNAME,0,0,MESG,2)
          ENDIF
        ENDDO
        CALL NEXTIME(jdate,jtime,tstep)
      ENDDO

!... Allocate the emission data IBUFF
      ALLOCATE ( IBUFF(NCOLS3D,NROWS3D,26,25,74) )

!... initial IBUFF
      IBUFF(:,:,:,:,:) = 0

!... store input date to IBUFF
!      DO s=1,74
!        DO t=1,25
!          DO z=1,8
!            IBUFF(:,:,z,t,ant_index(s)) = IBUFF(:,:,z,t,ant_index(s)) +
!     &                         ( VAR_POW(:,:,s,MONTH)*
!     &                   day_fac_pow*hour_fac_pow(t)*vert_fac_pow(z)+
!     &                           VAR_IND(:,:,s,MONTH)*
!     &                   day_fac_ind*hour_fac_ind(t)*vert_fac_ind(z)+
!     &                           VAR_RES(:,:,s,MONTH)*
!     &                   day_fac_res*hour_fac_res(t)*vert_fac_res(z)+
!     &                           VAR_TRA(:,:,s,MONTH)*
!     &                   day_fac_tra*hour_fac_tra(t)*vert_fac_tra(z)+
!     &                           VAR_SHP(:,:,s,MONTH)*
!     &                   day_fac_shp*hour_fac_shp(t)*vert_fac_shp(z) )*
!     &                           1000000/3600
!          ENDDO
!        ENDDO
!      ENDDO


!      DO s=1,1
!        DO t=1,25
!          DO z=1,8
!            IBUFF(:,:,z,t,agr_index(s)) = IBUFF(:,:,z,t,agr_index(s)) +
!     &                          VAR_AGR(:,:,s,MONTH)/
!     &                              MON_NUM(MONTH)*hour_fac_agr(t)*
!     &                              vert_fac_agr(z)*1000000/3600
!          ENDDO
!        ENDDO
!      ENDDO


      DO s=1,2
        DO t=1,25
          DO z=1,26
            IBUFF(:,:,z,t,oth_index(s)) = IBUFF(:,:,z,t,oth_index(s)) +
     &                         ( VAR_POW(:,:,s,MONTH)*
     &                   day_fac_pow*hour_fac_pow(t)*vert_fac_pow(z)+
     &                           VAR_IND(:,:,s,MONTH)*
     &                   day_fac_ind*hour_fac_ind(t)*vert_fac_ind(z)+
     &                           VAR_RES(:,:,s,MONTH)*
     &                   day_fac_res*hour_fac_res(t)*vert_fac_res(z)+
     &                          VAR_OTH(:,:,s,MONTH)/
     &                             MON_NUM(MONTH)/24*vert_fac_oth(z) )*
     &                          1000000/3600
          ENDDO
        ENDDO
      ENDDO

      DO s=1,31
        DO t=1,25
          DO z=1,26
            IBUFF(:,:,z,t,bio_index(s)) = IBUFF(:,:,z,t,bio_index(s)) +
     &                          VAR_BIO(:,:,s,t)*vert_fac_bio(z)
          ENDDO
        ENDDO
      ENDDO

!... 1 NO2
      IBUFF(:,:,:,:,1) = IBUFF(:,:,:,:,1) + VAR_EPD(:,:,:,16,:)*46/46.01
!... 2 NO
      IBUFF(:,:,:,:,2) = IBUFF(:,:,:,:,2) + VAR_EPD(:,:,:,15,:)*30/30.01
!... 3 HONO
      IBUFF(:,:,:,:,3) = IBUFF(:,:,:,:,3) + VAR_EPD(:,:,:,10,:)*47/47.02
!... 4 CO
      IBUFF(:,:,:,:,4) = IBUFF(:,:,:,:,4) + VAR_EPD(:,:,:,5,:)*28/28.01
!... 5 SO2
      IBUFF(:,:,:,:,5) = IBUFF(:,:,:,:,5) + VAR_EPD(:,:,:,28,:)*64/64.06
!... 6 SULF
      IBUFF(:,:,:,:,6) = IBUFF(:,:,:,:,6) + VAR_EPD(:,:,:,29,:)*98/98.08
!... 7 HCHO
      IBUFF(:,:,:,:,7) = IBUFF(:,:,:,:,7) + VAR_EPD(:,:,:,9,:)    !*0.40/1.00
!... 8 MEOH
      IBUFF(:,:,:,:,8) = IBUFF(:,:,:,:,8) + VAR_EPD(:,:,:,13,:)
!... 9 AACD
      IBUFF(:,:,:,:,9) = IBUFF(:,:,:,:,9) + VAR_EPD(:,:,:,33,:)*0.11/4.89
!... 10 PACD
      IBUFF(:,:,:,:,10) = IBUFF(:,:,:,:,10)
!... 11 RNO3
      IBUFF(:,:,:,:,11) = IBUFF(:,:,:,:,11)
!... 12 ACET
      IBUFF(:,:,:,:,12) = IBUFF(:,:,:,:,12) + VAR_EPD(:,:,:,21,:)*0.29/26.14
!... 13 CRES
      IBUFF(:,:,:,:,13) = IBUFF(:,:,:,:,13) + VAR_EPD(:,:,:,21,:)*0.05/26.14
!... 14 CCHO
      IBUFF(:,:,:,:,14) = IBUFF(:,:,:,:,14) + VAR_EPD(:,:,:,1,:)  !*0.16/0.36
!... 15 RCHO
      IBUFF(:,:,:,:,15) = IBUFF(:,:,:,:,15) + VAR_EPD(:,:,:,2,:)  !*0.08/0.33
!... 16 MEK
      IBUFF(:,:,:,:,16) = IBUFF(:,:,:,:,16) + VAR_EPD(:,:,:,21,:)*0.05/26.14
!... 17 FACD
      IBUFF(:,:,:,:,17) = IBUFF(:,:,:,:,17) + VAR_EPD(:,:,:,33,:)*0.02/4.89
!... 18 PRD2
      IBUFF(:,:,:,:,18) = IBUFF(:,:,:,:,18) + VAR_EPD(:,:,:,21,:)*0.03/26.14
!... 19 MGLY
      IBUFF(:,:,:,:,19) = IBUFF(:,:,:,:,19) + VAR_EPD(:,:,:,9,:)*0.09/1.00
!... 20 IPRD
      IBUFF(:,:,:,:,20) = IBUFF(:,:,:,:,20) + VAR_EPD(:,:,:,21,:)*0.02/26.14
!... 21 GLY
      IBUFF(:,:,:,:,21) = IBUFF(:,:,:,:,21) + VAR_EPD(:,:,:,9,:)*0.27/1.00
!... 22 BACL
      IBUFF(:,:,:,:,22) = IBUFF(:,:,:,:,22) + VAR_EPD(:,:,:,9,:)*0.01/1.00
!... 23 BALD
      IBUFF(:,:,:,:,23) = IBUFF(:,:,:,:,23) + VAR_EPD(:,:,:,31,:)*0.03/0.84
!... 24 MACR
      IBUFF(:,:,:,:,24) = IBUFF(:,:,:,:,24) + VAR_EPD(:,:,:,20,:)*0.01/1.45
!... 25 MVK
      IBUFF(:,:,:,:,25) = IBUFF(:,:,:,:,25) + VAR_EPD(:,:,:,21,:)*0.01/26.14
!... 26 ACRO
      IBUFF(:,:,:,:,26) = IBUFF(:,:,:,:,26) + VAR_EPD(:,:,:,20,:)*0.02/1.45
!... 27 ETHE
      IBUFF(:,:,:,:,27) = IBUFF(:,:,:,:,27) + VAR_EPD(:,:,:,6,:)  !*2.10/2.29
!... 28 PRPE
      IBUFF(:,:,:,:,28) = IBUFF(:,:,:,:,28) + VAR_EPD(:,:,:,20,:)*0.52/1.45
!... 29 BDE13
      IBUFF(:,:,:,:,29) = IBUFF(:,:,:,:,29) + VAR_EPD(:,:,:,11,:)*0.08/0.46
!... 30 ISOP
      IBUFF(:,:,:,:,30) = IBUFF(:,:,:,:,30) + VAR_EPD(:,:,:,12,:)
!... 31 APIN
      IBUFF(:,:,:,:,31) = IBUFF(:,:,:,:,31)
!... 32 ACYE
      IBUFF(:,:,:,:,32) = IBUFF(:,:,:,:,32) + VAR_EPD(:,:,:,21,:)*0.94/26.14
!... 33 BENZ
      IBUFF(:,:,:,:,33) = IBUFF(:,:,:,:,33) + VAR_EPD(:,:,:,3,:)
!... 34 TOLU
      IBUFF(:,:,:,:,34) = IBUFF(:,:,:,:,34) + VAR_EPD(:,:,:,31,:)*0.52/0.84
!... 35 MXYL
      IBUFF(:,:,:,:,35) = IBUFF(:,:,:,:,35) + VAR_EPD(:,:,:,34,:)*0.24/1.28
!... 36 OXYL
      IBUFF(:,:,:,:,36) = IBUFF(:,:,:,:,36) + VAR_EPD(:,:,:,34,:)*0.15/1.28
!... 37 PXYL
      IBUFF(:,:,:,:,37) = IBUFF(:,:,:,:,37) + VAR_EPD(:,:,:,34,:)*0.19/1.28
!... 38 B124
      IBUFF(:,:,:,:,38) = IBUFF(:,:,:,:,38) + VAR_EPD(:,:,:,34,:)*0.07/1.28
!... 39 ETOH
      IBUFF(:,:,:,:,39) = IBUFF(:,:,:,:,39) + VAR_EPD(:,:,:,8,:)  !*0.33/0.34
!... 40 ALK1
      IBUFF(:,:,:,:,40) = IBUFF(:,:,:,:,40) + VAR_EPD(:,:,:,7,:)  !*0.77/0.78
!... 41 ALK2
      IBUFF(:,:,:,:,41) = IBUFF(:,:,:,:,41) + VAR_EPD(:,:,:,21,:)*0.36/26.14
!... 42 ALK3
      IBUFF(:,:,:,:,42) = IBUFF(:,:,:,:,42) + VAR_EPD(:,:,:,21,:)*0.56/26.14
!... 43 ALK4
      IBUFF(:,:,:,:,43) = IBUFF(:,:,:,:,43) + VAR_EPD(:,:,:,21,:)*1.27/26.14
!... 44 ALK5
      IBUFF(:,:,:,:,44) = IBUFF(:,:,:,:,44) + VAR_EPD(:,:,:,21,:)*0.32/26.14
!... 45 SOAALK
      IBUFF(:,:,:,:,45) = IBUFF(:,:,:,:,45) + VAR_EPD(:,:,:,21,:)*0.88/26.14
!... 46 OLE1
      IBUFF(:,:,:,:,46) = IBUFF(:,:,:,:,46) + VAR_EPD(:,:,:,20,:)*0.53/1.45
!... 47 OLE2
      IBUFF(:,:,:,:,47) = IBUFF(:,:,:,:,47) + VAR_EPD(:,:,:,11,:)*0.97/0.46
!... 48 ARO1
      IBUFF(:,:,:,:,48) = IBUFF(:,:,:,:,48) + VAR_EPD(:,:,:,31,:)*0.20/0.84
!... 49 ARO2MN
      IBUFF(:,:,:,:,49) = IBUFF(:,:,:,:,49) + VAR_EPD(:,:,:,34,:)*0.51/1.28
!... 50 NAPH
      IBUFF(:,:,:,:,50) = IBUFF(:,:,:,:,50) + VAR_EPD(:,:,:,34,:)*0.02/1.28
!... 51 TERP
      IBUFF(:,:,:,:,51) = IBUFF(:,:,:,:,51) + VAR_EPD(:,:,:,30,:)
!... 52 SESQ
      IBUFF(:,:,:,:,52) = IBUFF(:,:,:,:,52)
!... 53 CL2
      IBUFF(:,:,:,:,53) = IBUFF(:,:,:,:,53)
!... 54 HCL
      IBUFF(:,:,:,:,54) = IBUFF(:,:,:,:,54) 
!... 55 PSO4
      IBUFF(:,:,:,:,55) = IBUFF(:,:,:,:,55) +
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.2027
!... 56 PNO3
      IBUFF(:,:,:,:,56) = IBUFF(:,:,:,:,56) +
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.0124
!... 57 PCL
      IBUFF(:,:,:,:,57) = IBUFF(:,:,:,:,57) +
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.0330 
!... 58 PNH4
      IBUFF(:,:,:,:,58) = IBUFF(:,:,:,:,58) + 
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.0146
!... 59 PNA
      IBUFF(:,:,:,:,59) = IBUFF(:,:,:,:,59) + 
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.0215
!... 60 PMG
      IBUFF(:,:,:,:,60) = IBUFF(:,:,:,:,60) + 
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.0059
!... 61 PK
      IBUFF(:,:,:,:,61) = IBUFF(:,:,:,:,61) +
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.0325
!... 62 PCA
      IBUFF(:,:,:,:,62) = IBUFF(:,:,:,:,62) +
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.0391
!... 63 POC
      IBUFF(:,:,:,:,63) = IBUFF(:,:,:,:,63) + VAR_EPD(:,:,:,26,:)
!... 64 PNCOM
      IBUFF(:,:,:,:,64) = IBUFF(:,:,:,:,64) +
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.1530 
!... 65 PEC
      IBUFF(:,:,:,:,65) = IBUFF(:,:,:,:,65) + VAR_EPD(:,:,:,22,:) 
!... 66 PFE
      IBUFF(:,:,:,:,66) = IBUFF(:,:,:,:,66) + 
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.0146
!... 67 PAL
      IBUFF(:,:,:,:,67) = IBUFF(:,:,:,:,67) + 
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.0291
!... 68 PSI
      IBUFF(:,:,:,:,68) = IBUFF(:,:,:,:,68) + 
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.0290
!... 69 PTI
      IBUFF(:,:,:,:,69) = IBUFF(:,:,:,:,69) + 
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.0017
!... 70 PMN
      IBUFF(:,:,:,:,70) = IBUFF(:,:,:,:,70) + 
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.0004
!... 71 PH2O
      IBUFF(:,:,:,:,71) = IBUFF(:,:,:,:,71) + 
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.0079
!... 72 PMOTHR
      IBUFF(:,:,:,:,72) = IBUFF(:,:,:,:,72) + 
     & (VAR_EPD(:,:,:,24,:)+VAR_EPD(:,:,:,25,:)+VAR_EPD(:,:,:,27,:))*0.4025
!... 73 PMC
      IBUFF(:,:,:,:,73) = IBUFF(:,:,:,:,73) + VAR_EPD(:,:,:,23,:)
!... 74 NH3
      IBUFF(:,:,:,:,74) = IBUFF(:,:,:,:,74) + VAR_EPD(:,:,:,14,:)


!... variable
!....              1        2        3         4        5   
      GCVARLIST=(/'NO2',   'NO',    'HONO',   'CO',    'SO2',
!....              6        7        8         9        10
     &            'SULF',  'HCHO',  'MEOH',   'AACD',  'PACD',
!....              11       12       13        14       15
     &            'RNO3',  'ACET',  'CRES',   'CCHO',  'RCHO',
!....              16       17       18        19       20     
     &            'MEK',   'FACD',  'PRD2',   'MGLY',  'IPRD',
!....              21       22       23        24       25
     &            'GLY',   'BACL',  'BALD',   'MACR',  'MVK',
!....              26       27       28        29       30
     &            'ACRO',  'ETHE',  'PRPE',   'BDE13', 'ISOP',
!....              31       32       33        34       35
     &            'APIN',  'ACYE',  'BENZ',   'TOLU',  'MXYL',
!....              36       37       38        39       40
     &            'OXYL',  'PXYL',  'B124',   'ETOH',  'ALK1',
!....              41       42       43        44       45
     &            'ALK2',  'ALK3',  'ALK4',   'ALK5',  'SOAALK',
!....              46       47       48        49       50
     &            'OLE1',  'OLE2',  'ARO1',   'ARO2MN','NAPH',
!....              51       52       53        54
     &            'TERP',  'SESQ',  'CL2',    'HCL'/)
!....              55       56       57        58       59 
      AEVARLIST=(/'PSO4',  'PNO3',  'PCL',    'PNH4',  'PNA',
!....              60       61       62        63       64
     &            'PMG',   'PK',    'PCA',    'POC',   'PNCOM',
!....              65       66       67        68       69
     &            'PEC',   'PFE',   'PAL',    'PSI',   'PTI',
!....              70       71       72        73 
     &            'PMN',   'PH2O',  'PMOTHR', 'PMC'/)
!....              74
      NRVARLIST=(/'NH3'/)
      print*,GCVARLIST,AEVARLIST,NRVARLIST

!-----------------------------------------------------------------------
!...... emission change test
!-----------------------------------------------------------------------
!      IBUFF(:,:,:,:,7:52)=IBUFF(:,:,:,:,7:52)*0.8  !VOC EMISSION*2
!      IBUFF(:,:,:,:,55:73)=IBUFF(:,:,:,:,55:73)*1.2
!      IBUFF(:,:,:,:,65) = 0

!-----------------------------------------------------------------------
!.....4) Store the emission data
!-----------------------------------------------------------------------
!... Rset jdate and jtime
      jdate = sdate + 62 ! convert 0701 to 0901 -- by Evan
      jtime = stime

!... set attribute
      FTYPE3D = GRDDED3
      SDATE3D = sdate + 62 ! convert 0701 to 0901 -- by Evan
      STIME3D = stime
      TSTEP3D = tstep
      MXREC3D = 25
      NLAYS3D = 26
      NVARS3D = 74
      VGTYP3D = 7
      VGTOP3D = 5000
      VGLVS3D(1:27) = (/1.0000, 0.9979, 0.9956, 0.9931, 0.9904, 0.9875,
     &                  0.9844, 0.9807, 0.9763, 0.9711, 0.9649, 0.9575,
     &                  0.9488, 0.9385, 0.9263, 0.9120, 0.8951, 0.8753,
     &                  0.8521, 0.8251, 0.7937, 0.7229, 0.6410, 0.4985,
     &                  0.2850, 0.0903, 0.0000/)
      VTYPE3D(1:NVARS3D) = M3REAL
      VNAME3D(1:54) = GCVARLIST(:)
      VNAME3D(55:73)= AEVARLIST(:)
      VNAME3D(74)   = NRVARLIST(1)
      VDESC3D  = VNAME3D
      DO s=1,54
        UNITS3D(s) = 'moles/s         '
      ENDDO
      DO s=55,73
        UNITS3D(s) = 'g/s             '
      ENDDO
      UNITS3D(74)  = 'moles/s         '

      write(*,*) FTYPE3D, SDATE3D, STIME3D, TSTEP3D, NCOLS3D, NROWS3D,
     &           NLAYS3D, NVARS3D, NTHIK3D, GDTYP3D, P_ALP3D, P_BET3D,
     &           P_GAM3D, XORIG3D, YORIG3D, XCELL3D, YCELL3D,
     &           XCENT3D, YCENT3D

      IF ( .NOT. OPEN3( EMIS_1, FSCREA3, PROGNAME ) ) THEN
        MESG = 'Could not open file '//TRIM(EMIS_1)
        CALL M3EXIT( PROGNAME, 0, 0, MESG, 2 )
      ENDIF

      DO t=1,25
        DO s=1,74
            IF ( .NOT. WRITE3(EMIS_1,VNAME3D(s),jdate,jtime,
     &                                        IBUFF(:,:,:,t,s)    )  ) THEN
               MESG = 'Error writing to file: '//TRIM(EMIS_1)
               CALL M3EXIT(PROGNAME,jdate,jtime,MESG,2)
            ENDIF
        ENDDO
        CALL NEXTIME(jdate,jtime,tstep)
      ENDDO

!=======================================================================
!...  End program
!=======================================================================
      ENDPROGRAM
